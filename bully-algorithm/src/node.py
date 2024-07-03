import grpc
import time

from node_grpc import node_service_pb2_grpc
from node_grpc.node_service_pb2 import NodeRequest, NodeResponse
from node_grpc.node_service_pb2_grpc import NodeServicer, NodeStub

from logging import Logger
from threading import Thread, Condition
from concurrent import futures
from typing import Dict
from enum import Enum


# constants
COORDINATOR_MESSAGE_TIMEOUT = 10.0
NODE_RESPONSE_TIMEOUT = 2.5
COORDINATOR_STATUS_INTERVAL = 5.0

class ElectionState(Enum):
    NOT_RUNNING = 1
    RUNNING = 2


class Node(NodeServicer):
    def __init__(
        self, 
        node_id: int,
        node_port: str, 
        other_nodes: Dict[int, str],
        logger: Logger,
    ):
        self.node_id: int = node_id
        self.node_port: str = node_port

        self.other_nodes: Dict[int, str] = other_nodes

        self.coordinator_id: int = None
        self.election_state: ElectionState = ElectionState.NOT_RUNNING

        self.election_state_cv: Condition = Condition()
        self.coordinator_id_cv: Condition = Condition()
        
        self.logger: Logger = logger


    def run_node(self):
        """
        Run the node server-side handler and client-side election cycle.
        """
        # start gRPC server
        grpc_server_handler = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        node_service_pb2_grpc.add_NodeServicer_to_server(self, grpc_server_handler)
        grpc_server_handler.add_insecure_port(f"[::]:{self.node_port}")
        grpc_server_handler.start()
        self.logger.info(f"Node {self.node_id} started gRPC server.")

        # run first election
        self._run_election()

        # check coordinator status loop
        coordinator_status_thread = Thread(target=self._check_coordinator_status, daemon=True)
        coordinator_status_thread.start()
        
        grpc_server_handler.wait_for_termination()

    def _run_election(self):
        """
        Run an election to choose a new coordinator.
        If no other nodes respond, the current node will coordinator message.
        If any other nodes respond, the current node will wait for a coordinator message to populate coordinator_id variable.
        """
        
        # set election_state flag to RUNNING
        self. election_state_cv.acquire()
        self.election_state = ElectionState.RUNNING
        self.election_state_cv.notify_all()
        self.election_state_cv.release()

        self.logger.info(f"Node {self.node_id} is running an election.")

        is_coordinator = True
        for other_node_id, other_node_host in self.other_nodes.items():
            if self.node_id < other_node_id:
                try:
                    other_node_stub = self. __create_node_stub(other_node_host)
                    other_node_stub.RunElection(NodeRequest(node_id=self.node_id), timeout=NODE_RESPONSE_TIMEOUT)
                    self.logger.info(f"Node {self.node_id} received an answer from Node {other_node_id}, so Node {self.node_id} can't be the coordinator anymore.")
                    is_coordinator = False
                except:
                    self.logger.error(f"Node {self.node_id} didn't get response from Node {other_node_id}.")

        self.coordinator_id_cv.acquire()
        if is_coordinator:
            self.coordinator_id = self.node_id
            self._send_coordinator_message()
        else:
            has_coordinator = lambda : self.coordinator_id is not None
            self.coordinator_id_cv.wait_for(has_coordinator, timeout=COORDINATOR_MESSAGE_TIMEOUT)
        self.coordinator_id_cv.release()

        # set election_state flag to NOT_RUNNING, even if coordinator was or wasn't elected
        self.election_state_cv.acquire()
        self.election_state = ElectionState.NOT_RUNNING
        self.election_state_cv.release()

        self.logger.info(f"Node {self.node_id} finished running an election")
        if self.coordinator_id is not None:
            self.logger.info(f"Node {self.coordinator_id} is the new elected coordinator")
        else:
            self.logger.info(f"Node {self.node_id} couldn't become coordinator, but no Node became coordinator.")


    def _check_coordinator_status(self):
        """
        Check if the coordinator is still alive.
        If coordinator is alive, do nothing.
        If coordinator is not alive, start a new election on a new thread.
        """
        self.logger.info(f"Node {self.node_id} started coordinator status check loop.")
        
        while True:
            self.coordinator_id_cv.acquire()
            if self.coordinator_id is not None and self.coordinator_id != self.node_id:
                self.logger.info(f"Node {self.node_id} checking coordinator Node {self.coordinator_id} status")
                try:
                    coordinator_host = self.other_nodes[self.coordinator_id]
                    coordinator_stub = self. __create_node_stub(coordinator_host)
                    coordinator_stub.GetCoordinatorStatus(NodeRequest(node_id=self.node_id), timeout=NODE_RESPONSE_TIMEOUT)
                except Exception as e:
                    self.logger.error(f"Node {self.node_id} could not check coordinator Node {self.coordinator_id} status. Error: {e}")
                    self.coordinator_id = None
            elif self.coordinator_id is None:
                self.logger.info(f"Node {self.node_id} has no coordinator.")
                election_thread = Thread(target=self._run_election)
                election_thread.start()
            self.coordinator_id_cv.release()
            time.sleep(COORDINATOR_STATUS_INTERVAL)

                
    def _send_coordinator_message(self):
        """
        Sets coordinator_id and sends a coordinator message request to all other nodes.
        """
        for node_id, node_host in self.other_nodes.items():
            try:
                node_stub = self. __create_node_stub(node_host)
                node_stub.ReceiveCoordinatorMessage(NodeRequest(node_id=self.node_id), timeout=NODE_RESPONSE_TIMEOUT)
            except Exception as e:
                self.logger.error(f"Coordinator Node {self.node_id} couldn't send coordinator message to Node {node_id}. Error: {e}")


    # ========================
    # gRPC server-side methods
    # ========================

    def RunElection(self, request: NodeRequest, context):
        """
        gRPC method to receive an election request from another node.
        Answer an election request from another node.
        If the current node is not running an election, it will answer ok and start an election.
        If the current node is running an election, it will answer ok.
        """
        self. election_state_cv.acquire()
        if self.election_state == ElectionState.RUNNING:
            self.logger.info(f"Node {self.node_id} is already running an election. Received election request from node {request.node_id}.")
        else:
            election_thread = Thread(target=self._run_election)
            election_thread.start()
            is_running = lambda : self.election_state == ElectionState.RUNNING
            self.election_state_cv.wait_for(is_running)
        self.election_state_cv.release()

        return NodeResponse()
    
    def ReceiveCoordinatorMessage(self, request: NodeRequest, context):
        """
        gRPC method to receive a coordinator message request from another node.
        Process a coordinator message request from another node and sets it as the current coordinator, if node is still running an election.
        Then, notifies condition variable to wake up threads waiting for a coordinator.
        If it is not running an election anymore, ignores message and logs a message.
        """
        self.coordinator_id_cv.acquire()
        self.coordinator_id = request.node_id
        self.coordinator_id_cv.notify_all()
        self.coordinator_id_cv.release()

        self.logger.info(f"Node {request.node_id} is the new elected leader/coordinator.")

        return NodeResponse()
    
    def GetCoordinatorStatus(self, request: NodeRequest, context):
        """
        gRPC method to receive a status check request from another node.
        """
        self.logger.info(f"Coordinator Node {self.node_id} status was checked by Node {request.node_id}.")
        return NodeResponse()
    

    # ========================
    #      helper methods
    # ========================

    def  __create_node_stub(self, node_host: int) -> NodeStub:
        """
        Get the gRPC client stub for the node with the given id.
        """
        channel = grpc.insecure_channel(node_host)
        grpc_stub = node_service_pb2_grpc.NodeStub(channel)
        return grpc_stub
import logging
import time
from typing import Any, Dict, List, Tuple

import grpc
import protobuf.service_pb2_grpc as service_pb2_grpc
import protobuf.service_pb2 as service_pb2
from joblib import dump, load

from lamport_clock.lamport_clock import LamportClock

class Storage(service_pb2_grpc.NodeCommunicationServiceServicer):
    def __init__(self, server_id: int):
        self.is_in_critical_section = False
        self.want_to_enter_critical_section = False
        self.request_queue: List[Tuple[service_pb2.UsageRequest, grpc.ServicerContext]] = []
        self.key_in_use: int = 0
        self.key_want_to_use: int = 0
        self.lamport_clock = LamportClock()
        self.id = server_id
        self.received_ok: List[bool] = [] # server_id: bool
        self.other_storages_addresses: Dict[int, str] = {
            1: "server1:50051",
            2: "server2:50052",
            3: "server3:50053",
            4: "server4:50054",
            5: "server5:50055",
        }
        self.my_request_time = 0

    def connect_to_other_storage(self, address: str):
        """
        This function connects to another storage server using gRPC.
        """
        while True:
            try:
                channel = grpc.insecure_channel(f'{address}')
                grpc.channel_ready_future(channel).result(timeout=10)
                return channel
            except grpc.FutureTimeoutError:
                logging.error(f"Connection to {address} failed. Retrying in 5 seconds...")
                time.sleep(5)

    def ReceiveOkMessage(self, request, context):
        """
        Receives an ok message from another storage server and appends it to the received_ok list.
        """
        logging.info(f"Server {self.id} received ok message from server {request.from_server_id}")
        self.received_ok.append(True)
        return service_pb2.UsageResponse(response="received ok")
    
    def send_ok_message(self, server_id: int):
        """
        Sends an ok message to another storage server.
        """
        logging.info(f"Server {self.id} sending ok message to server {server_id}")
        channel = self.connect_to_other_storage(self.other_storages_addresses[server_id])
        stub = service_pb2_grpc.NodeCommunicationServiceStub(channel)
        response = stub.ReceiveOkMessage(service_pb2.okMessage(from_server_id=self.id, response="ok"))
        return response

    def ReceiveRequestResourceUsage(self, request, context):
        """
        This function receives a request from another storage server to use a resource.
        The server will send an ok message if it is not in the critical section and does not want to enter the critical section.
        If the server is in the critical section, it will queue the request.
        """
        self.lamport_clock.update_clock(request.lamport_timestamp)
        self.lamport_clock.tick()

        if not self.is_in_critical_section and not self.want_to_enter_critical_section:
            logging.info(f"Server {self.id} not in critical section and not wanting to enter critical section, sending ok to server {request.server_id}")
            self.send_ok_message(request.server_id)
            return service_pb2.UsageResponse(response="send ok")
        elif self.is_in_critical_section and self.key_in_use == request.key:
            logging.info(f"Server {self.id} is in critical section and using key {self.key_in_use}, queuing request from server {request.server_id}")
            self.request_queue.append((request, context))
            return service_pb2.UsageResponse(response="queed request")
        elif self.want_to_enter_critical_section and self.key_want_to_use == request.key:
            if self.my_request_time < request.lamport_timestamp or (self.my_request_time == request.lamport_timestamp and self.id < request.server_id):
                logging.info(f"Server {self.id} wants to enter critical section and wants to use key {self.key_want_to_use} but server {request.server_id} has priority, queuing request")
                self.send_ok_message(request.server_id)
                return service_pb2.UsageResponse(response="send ok")
            else:
                logging.info(f"Server {self.id} wants to enter critical section and wants to use key {self.key_want_to_use} and has priority, queuing request from server {request.server_id}")
                self.request_queue.append((request, context))
                return service_pb2.UsageResponse(response="queed request")
        

    def request_resource_usage(self, want_to_use_key: int):
        """
        Sends a request to all other storage servers to use a resource.
        When all servers have responded with an ok message, the server will enter the critical section.
        Until then, the server will wait.
        """
        logging.info(f"Server {self.id} requesting resource usage for key {want_to_use_key}")
        self.lamport_clock.tick()
        self.my_request_time = self.lamport_clock.get_clock()

        for storage_server_id, storage_address in self.other_storages_addresses.items():
            if storage_server_id != self.id:
                logging.info(f"Server {self.id} requesting resource usage for key {want_to_use_key} to server {storage_server_id}")
                channel = self.connect_to_other_storage(storage_address)
                stub = service_pb2_grpc.NodeCommunicationServiceStub(channel)
                response = stub.ReceiveRequestResourceUsage(service_pb2.UsageRequest(
                    lamport_timestamp=self.lamport_clock.get_clock(), 
                    server_id=self.id, 
                    key=want_to_use_key
                ))

        self.wait_for_ok_messages()
        self.is_in_critical_section = True
        logging.info(f"Server {self.id} has entered critical section")


    def wait_for_ok_messages(self):
        """
        Waits for all other storage servers to respond with an ok message.
        """
        logging.info(f"Server {self.id} waiting for ok messages")
        while len(self.received_ok) < 4:
            time.sleep(1)

    def process_request_queue(self):
        """
        Sends and Ok message for each request in the request queue.
        """
        logging.info(f"Server {self.id} Processing request queue of length {len(self.request_queue)}")
        while self.request_queue:
            request, context = self.request_queue.pop(0)
            self.send_ok_message(request.server_id)
            logging.info(f"Server {self.id} sending ok message to server {request.server_id} that was in the queue")

    def set_value(self, key, value):
        """
        Critical section where the server sets a value in a key.
        """
        self.want_to_enter_critical_section = True
        self.key_want_to_use = key
        self.request_resource_usage(key)
        self.key_in_use = key
        data = load("data.pkl")
        data[key] = value
        time.sleep(7)
        logging.info(f"data: {data}")
        dump(data, "data.pkl")
        self.key_in_use = 0
        self.key_want_to_use = 0
        self.is_in_critical_section = False
        self.want_to_enter_critical_section = False
        self.process_request_queue()

    def get_value(self, key):
        data = load("data.pkl")
        if key not in data:
            raise KeyError(f"Key {key} not found")
        return data.get(key)
    
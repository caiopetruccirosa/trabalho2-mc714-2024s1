import grpc
from concurrent import futures
import time
import os
import logging
import random
# Import the generated classes
import protobuf.service_pb2_grpc as service_pb2_grpc
import protobuf.service_pb2 as service_pb2

from storage.storage import Storage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

"""
This file creates a gRPC server that communicates with other servers.
"""

def serve():
    # Create a gRPC server
    server_id = int(os.getenv('SERVER_ID'))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    service = Storage(server_id)
    service_pb2_grpc.add_NodeCommunicationServiceServicer_to_server(service, server)
    
    # Determine the server's port
    port = os.getenv('SERVER_PORT')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logging.info(f"Server started, listening on port {port}")

    # Periodically try to set a valut in a key
    keys_to_use = [3]
    values_to_use = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    time.sleep(5)
    while True:
        key = random.choice(keys_to_use)
        value = random.choice(values_to_use)
        time.sleep(random.randint(10, 25))
        service.set_value(key, value)
        time.sleep(2)

if __name__ == '__main__':
    serve()

import grpc
from concurrent import futures
import time
import os
import logging
# Import the generated classes
import protobuf.service_pb2_grpc as service_pb2_grpc
import protobuf.service_pb2 as service_pb2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a class to define the server functions, derived from
# service_pb2_grpc.MyServiceServicer
class MyServiceServicer(service_pb2_grpc.MyServiceServicer):
    def ReceiveMessage(self, request, context):
        SERVER_ID = os.getenv('SERVER_ID')
        logging.info(f"{request.message}")
        return service_pb2.MessageReply(response=f'im server {SERVER_ID} and received your message!')
    
    def SendMessage(self, host, port):
        channel = wait_for_other_server(host, port)
        stub = service_pb2_grpc.MyServiceStub(channel)
        SERVER_ID = os.getenv('SERVER_ID')
        return stub.ReceiveMessage(service_pb2.MessageRequest(message=f'Message from server {SERVER_ID} to server {host}:{port}'))

def wait_for_other_server(host, port):
    while True:
        try:
            channel = grpc.insecure_channel(f'{host}:{port}')
            grpc.channel_ready_future(channel).result(timeout=10)
            return channel
        except grpc.FutureTimeoutError:
            logging.error(f"Connection to {host}:{port} failed. Retrying in 5 seconds...")
            time.sleep(5)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    service = MyServiceServicer()
    service_pb2_grpc.add_MyServiceServicer_to_server(service, server)
    
    port = os.getenv('SERVER_PORT', '50051')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logging.info(f"Server started, listening on port {port}")

    # Determine the other server's address and port
    other_server_host = os.getenv('OTHER_SERVER_HOST', 'localhost')
    other_server_port = os.getenv('OTHER_SERVER_PORT', '50052')

    # Periodically send messages to the other server
    while True:
        response = service.SendMessage(other_server_host, other_server_port)
        logging.info(f"Received response: {response.response}")
        time.sleep(15)

if __name__ == '__main__':
    serve()

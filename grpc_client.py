import grpc
from rpc.services.source_pb2 import SourceRequest
import rpc.services.source_pb2_grpc as source_pb2_grpc
from settings import GRPC_ADDRESS


def run():
    try:
        # Connect to the gRPC server with channel options for better reliability
        with grpc.insecure_channel(
            GRPC_ADDRESS,
            options=[
                ("grpc.enable_retries", 1),
            ],
        ) as channel:
            stub = source_pb2_grpc.SourceServiceStub(channel)

            # Create a request
            request = SourceRequest(
                url="https://www.up.ac.za/news",
                containsAfricaContent=True,
                containsAiContent=False,
            )

            # Call the RPC method with timeout
            response = stub.addSource(request, timeout=200)

            print(f"Response from server: {response.message}")

    except grpc.RpcError as e:
        print(f"RPC failed with {e.code()}: {e.details()}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    run()

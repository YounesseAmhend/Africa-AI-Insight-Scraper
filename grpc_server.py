import asyncio
from concurrent.futures import ThreadPoolExecutor
import grpc
import rpc.services.source_pb2_grpc as source_pb2_grpc
from services.source_service import SourceService
from settings import GRPC_ADDRESS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def serve() -> None:
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    source_pb2_grpc.add_SourceServiceServicer_to_server(SourceService(), server)
    server.add_insecure_port(GRPC_ADDRESS)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        logger.info("Starting gRPC server...")
        serve()
    except Exception as e:
        logger.error(f"Server crashed: {str(e)}", exc_info=True)

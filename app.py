from concurrent.futures import ThreadPoolExecutor

import grpc

from grpc_services.source_service import SourceService
from protos import source_pb2_grpc
from settings import PORT
from utils.logger import logger



def serve() -> None:

    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    source_pb2_grpc.add_SourceServiceServicer_to_server(SourceService(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        logger.info("Starting gRPC server...")
        serve()
    except Exception as e:
        logger.error(f"Server crashed: {str(e)}", exc_info=True)

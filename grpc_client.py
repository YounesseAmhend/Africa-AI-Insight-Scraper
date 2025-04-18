import grpc
from protos import source_pb2_grpc
from protos import source_pb2

from protos.source_pb2 import ScrapeRequest, SourceRequest
from settings import GRPC_ADDRESS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(GRPC_ADDRESS)
        self.stub = source_pb2_grpc.SourceServiceStub(self.channel)

    def add_source(self, url: str, contains_ai: bool, contains_africa: bool):
        request = SourceRequest(
            url=url,
            containsAiContent=contains_ai,
            containsAfricaContent=contains_africa,
        )
        try:
            response = self.stub.addSource(request)
            logger.info(f"Add source response: {response.message}")
            return response
        except grpc.RpcError as e:
            logger.error(f"Failed to add source: {e}")
            return None

    def scrape(self):
        request = ScrapeRequest()
        try:
            response = self.stub.scrape(request)
            logger.info(f"Scrape response: {response.message}")
            return response
        except grpc.RpcError as e:
            logger.error(f"Failed to scrape: {e}")
            return None


def test_grpc_functions():
    client = SourceClient()

    # Test addSource
    logger.info("Testing addSource...")
    # add_response = client.add_source(
    #     url="https://www.up.ac.za/news",
    #     contains_ai=False,
    #     contains_africa=True,
    # )

    # Test scrape
    logger.info("Testing scrape...")
    scrape_response = client.scrape()


if __name__ == "__main__":
    try:
        logger.info("Starting gRPC client tests...")
        test_grpc_functions()
    except Exception as e:
        logger.error(f"Client tests failed: {str(e)}", exc_info=True)

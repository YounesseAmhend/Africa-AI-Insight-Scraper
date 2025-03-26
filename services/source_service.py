import logging
import time
from config.db import DatabaseConfig

from grpc import ServicerContext

from main import scrape_news, try_until
from rpc.services.source_pb2  import SourceRequest, SourceResponse
from rpc.services.source_pb2_grpc import SourceServiceServicer

from repositories.source_repository import SourceRepository


class SourceService(SourceServiceServicer):

    def addSource(
        self,
        request: SourceRequest,
        context: ServicerContext,
    ) -> SourceResponse:

        url = request.url


        start_time = time.time()

        result = try_until(
            lambda: scrape_news(url),
            max_retries=3,
        )

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"Scraping completed in {elapsed_time:.2f} seconds")

        selector = result["selector"]  # type: ignore

        if selector:
            db_config = DatabaseConfig()
            db_config.create_tables()  # Ensure tables exist

            source_repo = SourceRepository(db_config)

            try:
                # Store source with selector
                record_id = source_repo.add_source(
                    selector=selector,
                    source = request,
                    
                )

                result["db_record_id"] = record_id  # type: ignore

            except Exception as e:
                logging.error(f"Failed to store source: {e}")

        return SourceResponse(
            message=str(result), #* Just for testing purposes otherwise this is completely stupid
        )

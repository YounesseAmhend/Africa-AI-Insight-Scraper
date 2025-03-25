# services/source_service.py
import logging
import time
from config.db import DatabaseConfig

from main import scrape_news, try_until
import my_grpc.services.source_pb2 as pb
import my_grpc.services.source_pb2_grpc as pb_grpc
import grpc

from repositories.source_repository import SourceRepository


class SourceService(pb_grpc.SourceServiceServicer):
    def addSource(
        self,
        request: pb.SourceRequest,
        context,
    ) -> pb.SourceResponse:
        url = request.url
        trigger_africa = not request.containsAfricaContent
        trigger_ai = not request.containsAiContent

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
                    url=url,
                    selector=selector,
                    trigger_africa=trigger_africa,
                    trigger_ai=trigger_ai,
                )

                result["db_record_id"] = record_id  # type: ignore

            except Exception as e:
                logging.error(f"Failed to store source: {e}")

        return pb.SourceResponse(message="Failed")

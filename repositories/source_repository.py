import datetime

from psycopg2.extras import Json

from config.db import DatabaseConfig
from dtypes.selector import Selector
from models.enums.scrape_status import ScrapeStatus
from models.source import Source, SourceUpdate
from protos.source_pb2 import SourceRequest
from utils.logger import logger


class SourceRepository:
    """
    Service for managing source-related database operations
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize SourceService

        :param db_config: DatabaseConfig instance
        """
        self.db_config = DatabaseConfig()

    def update_selector(
        self,
        id: int,
        selector: Selector,
    ) -> None:
        """
        Update selector for a given source ID

        :param id: Source ID to update
        :param selector: New selector dictionary
        """
        update_query = """
        UPDATE sources
        SET selector = %s
        WHERE id = %s
        """
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        update_query,
                        (Json(selector), id),
                    )
                conn.commit()
                logger.info(f"Selector updated for source ID: {id}")
        except Exception as e:
            logger.error(f"Error updating selector: {e}")
            raise

    def get_sources(self) -> list[Source]:
        """
        Retrieve all sources from the database

        :return: List of Source objects
        """
        select_query = """
        SELECT id, url, selector, triggerAfrica, triggerAi, createdAt, updatedAt
        FROM sources
        """
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(select_query)
                    results = cur.fetchall()
                    sources = []
                for row in results:
                    print(f"\n\nRow {row}\n\n\n")

                    source = Source(
                        id=row[0],
                        url=row[1],
                        selector=dict(row[2]) if row[2] else {},
                        triggerAfrica=row[3],
                        triggerAi=row[4],
                        createdAt=row[5].isoformat(),
                        updateAt=row[6].isoformat() if row[6] else None,
                    )
                    sources.append(source)
                return sources

        except Exception as e:
            logger.error(f"Error retrieving sources: {e}")
            raise
        
    def set_status(self, id: int, status: ScrapeStatus) -> None:
        """
        Set the scrape status for a given source ID

        :param id: Source ID to update
        :param status: ScrapeStatus enum value to set
        """
        update_query = """
        UPDATE sources
        SET status = %s
        WHERE id = %s
        """
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        update_query,
                        (status.value, id),
                    )
                conn.commit()
                logger.info(f"Status updated to {status.value} for source ID: {id}")
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            raise
                

    def get_source(self, id: int) -> Source:
        """
        Retrieve a single source by ID from the database

        :param id: Source ID to retrieve
        :return: Source object
        """
        select_query = """
        SELECT id, url, selector, triggerAfrica, triggerAi, createdAt, updatedAt
        FROM sources
        WHERE id = %s
        """
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(select_query, (id,))
                    row = cur.fetchone()
                    if row:
                        return Source(
                            id=row[0],
                            url=row[1],
                            selector=dict(row[2]) if row[2] else {},
                            triggerAfrica=row[3],
                            triggerAi=row[4],
                            createdAt=row[5].isoformat(),
                            updateAt=row[6].isoformat() if row[6] else None,
                        )
                    raise ValueError(f"Source with ID {id} not found")
        except Exception as e:
            logger.error(f"Error retrieving source: {e}")
            raise

    def update_at(
        self,
        id: int,
        time: datetime.datetime,
    ) -> None:
        """
        Update the timestamp for a given source ID

        :param id: Source ID to update
        :param time: New datetime to set
        """
        update_query = """
        UPDATE sources
        SET updatedAt = %s
        WHERE id = %s
        """
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        update_query,
                        (time.isoformat(), id),
                    )
                conn.commit()
                logger.info(f"Timestamp updated for source ID: {id}")
        except Exception as e:
            logger.error(f"Error updating timestamp: {e}")
            raise

    def upsert_source(
        self,
        selector: Selector,
        source: SourceRequest | SourceUpdate,
    ) -> int:
        """
        Insert or update source with selector

        :param url: Source URL
        :param selector: Selector dictionary
        :param trigger_africa: Africa trigger flag
        :param trigger_ai: AI trigger flag
        :return: Inserted/Updated record ID
        """

        status = ScrapeStatus.UNAVAILABLE.value if not selector else ScrapeStatus.AVAILABLE.value
        insert_query = """
        INSERT INTO sources 
            (url, selector, triggerAfrica, triggerAi, createdAt, status)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
        ON CONFLICT (url) DO UPDATE SET
            selector = EXCLUDED.selector,
            triggerAfrica = EXCLUDED.triggerAfrica, 
            triggerAi = EXCLUDED.triggerAi,
            createdAt = CURRENT_TIMESTAMP,
            status = EXCLUDED.status
        RETURNING id
        """
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        insert_query,
                        (
                            source.url,
                            Json(selector),
                            not source.containsAfricaContent,
                            not source.containsAiContent,
                            status,
                        ),
                    )
                    record_id: int = cur.fetchone()[0]
                conn.commit()
                logger.info(f"Source stored/updated for URL: {source.url}")
                return record_id
        except Exception as e:
            logger.info(f"Error storing source: {e}")
            raise

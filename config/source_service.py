# services/source_service.py
import logging
from psycopg2.extras import Json
from config.db import DatabaseConfig

class SourceService:
    """
    Service for managing source-related database operations
    """
    def __init__(self, db_config: DatabaseConfig):
        """
        Initialize SourceService
        
        :param db_config: DatabaseConfig instance
        """
        self.db_config = db_config

    def upsert_source(
        self, 
        url: str, 
        selector: dict, 
        trigger_africa: bool = False, 
        trigger_ai: bool = False
    ):
        """
        Insert or update source with selector
        
        :param url: Source URL
        :param selector: Selector dictionary
        :param trigger_africa: Africa trigger flag
        :param trigger_ai: AI trigger flag
        :return: Inserted/Updated record ID
        """
        upsert_query = """
        INSERT INTO sources 
            (url, selector, trigger_africa, trigger_ai, updated_at)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (url) DO UPDATE 
        SET 
            selector = EXCLUDED.selector,
            trigger_africa = EXCLUDED.trigger_africa,
            trigger_ai = EXCLUDED.trigger_ai,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        upsert_query, 
                        (
                            url, 
                            Json(selector), 
                            trigger_africa, 
                            trigger_ai
                        )
                    )
                    record_id = cur.fetchone()[0]
                conn.commit()
                logging.info(f"Source stored/updated for URL: {url}")
                return record_id
        
        except Exception as e:
            logging.error(f"Error storing source: {e}")
            raise
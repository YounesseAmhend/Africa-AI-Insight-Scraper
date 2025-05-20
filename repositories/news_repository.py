import datetime

from config.db import DatabaseConfig
from models.news import NewsAdd
from utils.checker import Checker
from utils.logger import logger


class NewsRepository:
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

    def add_news(
        self,
        data: NewsAdd,
    ) -> None:
        """
        Add a new news article to the database

        :param source_id: ID of the source this news belongs to
        :param data: NewsAddRequest containing news data
        """
        query = """
            INSERT INTO news (
                sourceId,
                categoryId,
                title,
                url,
                authorId,
                body,
                postDate,
                imageUrl,
                createdAt
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
            ) ON CONFLICT (title) DO UPDATE SET body = EXCLUDED.body
        """

        # Convert post_date from string to datetime if it exists
        date = Checker.get_date(data.postDate or '')
        if date is None:
            logger.info(f"Could not parse date: {data.postDate}")
        params = (
            data.sourceId,
            data.categoryId,
            data.title,
            data.url,
            data.authorId,
            data.body,
            date,
            data.imageUrl,
        )

        logger.info(f"Preparing to insert news article with params: {params}")

        with self.db_config.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    logger.info("Executing SQL query to insert news article")
                    cursor.execute(query, params)
                    conn.commit()
                    logger.info("Successfully inserted news article")
                except Exception as e:
                    logger.error(f"Failed to insert news article: {str(e)}")
                    raise

import datetime
import logging
from config.db import DatabaseConfig
from models.news import NewsAdd
from utils.checker import Checker


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
            )
        """

        # Convert post_date from string to datetime if it exists
        date = Checker.get_date(data.postDate)
        if date is None:
            logging.info(f"Could not parse date: {data.postDate}")
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

        logging.info(f"Preparing to insert news article with params: {params}")

        with self.db_config.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    logging.info("Executing SQL query to insert news article")
                    cursor.execute(query, params)
                    conn.commit()
                    logging.info("Successfully inserted news article")
                except Exception as e:
                    logging.error(f"Failed to insert news article: {str(e)}")
                    raise

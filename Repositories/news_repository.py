import datetime
import logging
from config.db import DatabaseConfig
from models.news import NewsAdd


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
                title,
                url,
                authorId,
                body,
                postDate,
                imageUrl
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (url) DO NOTHING
        """

        date_formats = [
            "%Y-%m-%dT%H:%M:%S",  # ISO 8601
            "%Y-%m-%d %H:%M:%S",  # Common datetime format
            "%Y/%m/%d %H:%M:%S",  # Slash separated
            "%d/%m/%Y %H:%M:%S",  # European format
            "%m/%d/%Y %H:%M:%S",  # US format
            "%Y-%m-%d",  # Date only
            "%d %b %Y",  # 01 Jan 2023
            "%b %d, %Y",  # Jan 01, 2023
            "%d %B %Y",  # 01 January 2023
            "%B %d, %Y",  # January 01, 2023
        ]
        date_prefixes = [
            "Posted on",
            "Posted",
            "Published on",
            "Published",
            "Last updated on",
            "Last updated",
            "Updated on",
            "Updated",
            "Created on",
            "Created",
            "Date:",
            "Time:",
            ":",
        ]
        for prefix in date_prefixes:
            post_date = data.postDate.replace(prefix, "").strip()

        date = None
        for fmt in date_formats:
            try:
                date = datetime.datetime.strptime(
                    post_date, fmt
                )
                break
            except ValueError:
                continue

        # Convert post_date from string to datetime if it exists
        if date is None:
            logging.error(f"Could not parse date: {post_date}")

        params = (
            data.sourceId,
            data.title,
            data.url,
            data.authorId,
            data.body,
            date,
            data.imageUrl,
        )

        with self.db_config.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()

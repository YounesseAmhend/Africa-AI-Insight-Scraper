import datetime
from config.db import DatabaseConfig
from rpc.protos.news_pb2 import NewsAddRequest






class NewsRepository:
    """
    Service for managing source-related database operations
    """

    TABLE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS news (
        id SERIAL PRIMARY KEY,
        sourceId INTEGER NOT NULL REFERENCES sources(id),
        title TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        authorId INTEGER REFERENCES authors(id),
        body TEXT NOT NULL,
        postDate TIMESTAMP WITH TIME ZONE,
        imageUrl TEXT,
        createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)
    """

    def __init__(
        self,
        db_config: DatabaseConfig,
    ) -> None:
        """
        Initialize SourceService

        :param db_config: DatabaseConfig instance
        """
        self.db_config = db_config

    def add_news(
        self,
        source_id: int,
        data: NewsAddRequest,
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

        # Convert post_date from string to datetime if it exists
        post_date = (
            datetime.datetime.fromisoformat(data.postDate) if data.postDate else None
        )

        params = (
            source_id,
            data.title,
            data.url,
            data.authorId if data.HasField("authorId") else None,
            data.body,
            post_date,
            data.imageUrl if data.HasField("imageUrl") else None,
        )

        with self.db_config.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()

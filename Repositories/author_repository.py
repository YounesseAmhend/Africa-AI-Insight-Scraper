from config.db import DatabaseConfig
from rpc.protos.author_pb2 import AuthorResponse

class AuthorRepository:
    TABLE_SCHEMA = """
        CREATE TABLE IF NOT EXISTS authors (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            url TEXT UNIQUE,
            createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        )
        """

    def __init__(self, db_config: DatabaseConfig) -> None:
        """
        Initialize AuthorRepository

        :param db_config: DatabaseConfig instance
        """
        self.db_config = db_config

    def get_or_create_author(self, author: AuthorResponse) -> int:
        """
        Get or create an author in the database

        :param name: Author's name
        :param url: Author's URL (optional)
        :return: ID of the existing or newly created author
        """
        # First try to get existing author
        query = "SELECT id FROM authors WHERE name = %s"
        with self.db_config.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (author.name,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                
                # If not found, create new author
                query = """
                    INSERT INTO authors (name, url)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id
                """
                cursor.execute(query, (author.name, author.url))
                conn.commit()
                return cursor.fetchone()[0]
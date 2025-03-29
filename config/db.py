import os
from numpy import source
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import logging

from Repositories.author_repository import AuthorRepository
from Repositories.news_repository import NewsRepository
from Repositories.source_repository import SourceRepository


class DatabaseConfig:
    """
    Centralized database configuration and connection management
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, min_connections: int = 1, max_connections: int = 10):
        """
        Initialize database connection pool

        :param host: Database host
        :param database: Database name
        :param user: Database username
        :param password: Database password
        :param port: Database port
        :param sslmode: SSL mode for connection
        :param min_connections: Minimum connections in pool
        :param max_connections: Maximum connections in pool
        """
        host: str | None = os.getenv("DB_HOST")
        database: str | None = os.getenv("DB_NAME")
        user: str | None = os.getenv("DB_USER")
        password: str | None = os.getenv("DB_PASSWORD")
        port_str: str | None = os.getenv("DB_PORT")
        sslmode: str | None = os.getenv("DB_SSLMODE")

        if None in (host, database, user, password, port_str, sslmode):
            raise ValueError(
                "One or more required database environment variables are not set"
            )

        port: int = int(port_str)  # type: ignore
        if self._initialized:
            return

        self.connection_params = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port,
            "sslmode": sslmode,
        }

        # Create connection pool
        try:
            self.connection_pool = SimpleConnectionPool(
                min_connections, max_connections, **self.connection_params
            )
        except Exception as e:
            logging.error(f"Database connection pool error: {e}")
            raise

        self._initialized = True

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections

        :yield: Database connection
        """
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def create_tables(self):
        """
        Create necessary tables if they don't exist
        """

        TABLES: list[str] = [
            SourceRepository.TABLE_SCHEMA,
            AuthorRepository.TABLE_SCHEMA,
            NewsRepository.TABLE_SCHEMA,
        ]
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    for table in TABLES:
                        cur.execute(table)
                conn.commit()
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            raise

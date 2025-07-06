import os
from contextlib import contextmanager

from constants import (
    AUTHORS_TABLE_SCHEMA,
    CATEGORY_TABLE_SCHEMA,
    NEWS_TABLE_SCHEMA,
    SOURCE_TABLE_SCHEMA,
    STATISTICS_TABLE_SCHEMA,
)
from psycopg2.pool import SimpleConnectionPool
from utils.logger import logger

from scraper.settings import WORKERS_COUNT


class DatabaseConfig:
    """
    Centralized database configuration and connection management
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConfig, cls).__new__(cls)
            cls._instance._initialized = False
            # Move create_tables to after initialization
        return cls._instance

    def __init__(self, min_connections: int = None, max_connections: int = None):
        """
        Initialize database connection pool
        """
        if self._initialized:
            return

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
            min_connections = min_connections or int(os.getenv("DB_POOL_MIN", 1))
            max_connections = max_connections or int(
                os.getenv("DB_POOL_MAX", WORKERS_COUNT)
            )
            self.connection_pool = SimpleConnectionPool(
                min_connections, max_connections, **self.connection_params
            )
        except Exception as e:
            logger.error(f"Database connection pool error: {e}")
            raise

        self._initialized = True
        # Now that we're initialized, create tables
        self.create_tables()

    @contextmanager
    def get_connection(self):
        if not hasattr(self, "connection_pool"):
            raise AttributeError("Connection pool not initialized")

        conn = self.connection_pool.getconn()
        logger.debug(f"Acquired connection: {conn}")
        try:
            yield conn
        finally:
            logger.debug(f"Releasing connection: {conn}")
            self.connection_pool.putconn(conn)

    def create_tables(self):
        """
        Create necessary tables if they don't exist
        """
        if not hasattr(self, "connection_pool"):
            return

        TABLES: list[str] = [
            SOURCE_TABLE_SCHEMA,
            AUTHORS_TABLE_SCHEMA,
            NEWS_TABLE_SCHEMA,
            CATEGORY_TABLE_SCHEMA,
            STATISTICS_TABLE_SCHEMA,
        ]
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    for table in TABLES:
                        cur.execute(table)
                conn.commit()
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

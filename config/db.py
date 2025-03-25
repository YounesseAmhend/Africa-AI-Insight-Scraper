# config/database.py
import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import logging

class DatabaseConfig:
    """
    Centralized database configuration and connection management
    """
    def __init__(
        self, 
        host: str = os.getenv('DB_HOST', 'localhost'),
        database: str = os.getenv('DB_NAME', 'aiafriqua'),
        user: str = os.getenv('DB_USER', 'postgres'),
        password: str = os.getenv('DB_PASSWORD', 'postgres'),
        port: int = int(os.getenv('DB_PORT', 5432)),
        min_connections: int = 1,
        max_connections: int = 10
    ):
        """
        Initialize database connection pool
        
        :param host: Database host
        :param database: Database name
        :param user: Database username
        :param password: Database password
        :param port: Database port
        :param min_connections: Minimum connections in pool
        :param max_connections: Maximum connections in pool
        """
        self.connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        
        # Create connection pool
        try:
            self.connection_pool = SimpleConnectionPool(
                min_connections, 
                max_connections, 
                **self.connection_params
            )
        except Exception as e:
            logging.error(f"Database connection pool error: {e}")
            raise

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
        create_sources_table = """
        CREATE TABLE IF NOT EXISTS sources (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            selector JSONB,
            trigger_africa BOOLEAN DEFAULT FALSE,
            trigger_ai BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_sources_table)
                conn.commit()
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            raise
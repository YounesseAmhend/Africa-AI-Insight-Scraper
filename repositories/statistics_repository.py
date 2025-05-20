from config.db import DatabaseConfig
from models.statistics import Statistics


class StatisticsRepository:

    def __init__(
        self,
    ) -> None:
        """
        Initialize StatisticsRepository

        :param db_config: DatabaseConfig instance
        """
        self.db_config = DatabaseConfig()

    def get_updated_date(self, name: str) -> str | None:
        """
        Get the updated date for a given statistics name

        :param name: Statistics name
        :return: Updated date as string or None if not found
        """
        query = "SELECT updatedAt FROM statistics WHERE name = %s"
        with self.db_config.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name,))
                result = cursor.fetchone()
                return result[0] if result else None

    def create_or_update_statistics(self, statistics: Statistics) -> int:
        """
        Create or update statistics in the database

        :param statistics: Statistics object
        :return: ID of the existing or newly created statistics
        """
        # First try to get existing statistics
        query = "SELECT id, updatedAt FROM statistics WHERE name = %s"
        with self.db_config.get_connection() as conn:
            with conn.cursor() as cursor:
                # Upsert statistics including stats JSONB
                query = """
                    INSERT INTO statistics (name, stats, updatedAt)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (name) DO UPDATE SET
                        stats = EXCLUDED.stats,
                        updatedAt = CURRENT_TIMESTAMP
                    RETURNING id
                """
                cursor.execute(query, (statistics.name, statistics.stats))
                conn.commit()
                return cursor.fetchone()[0]

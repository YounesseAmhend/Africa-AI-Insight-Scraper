from config.db import DatabaseConfig
from models.category import Category


class CategoryRepository:

    def __init__(
        self,
    ) -> None:
        """
        Initialize CategoryRepository

        :param db_config: DatabaseConfig instance
        """
        self.db_config = DatabaseConfig()

    def get_or_create_category(self, category: Category) -> int:
        """
        Get or create a category in the database

        :param name: Category's name
        :return: ID of the existing or newly created category
        """


        # First try to get existing category
        query = "SELECT id FROM categories WHERE name = %s"
        with self.db_config.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (category.name,))
                result = cursor.fetchone()
                if result:
                    return result[0]

                # If not found, create new category
                query = """
                    INSERT INTO categories (name, updatedAt)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id
                """
                cursor.execute(query, (category.name, category.updatedAt))
                conn.commit()
                return cursor.fetchone()[0]

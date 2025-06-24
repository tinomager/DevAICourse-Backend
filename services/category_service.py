from typing import List
from fastapi import HTTPException
from generated.models.category import Category
from db import db_pool

class CategoryService:
    @staticmethod
    def create_category(category: Category) -> Category:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            if category.id is None or category.id == 0:
                cursor.execute('SELECT MAX(id) FROM categories')
                max_id_row = cursor.fetchone()
                category.id = (max_id_row[0] or 0) + 1

            # Insert category into database
            cursor.execute('INSERT INTO categories (id, name) VALUES (?, ?)',
                           (category.id, category.name))
            conn.commit()

        return category

    @staticmethod
    def update_category(category: Category) -> Category:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            # Update category in database
            cursor.execute('''
                UPDATE categories
                SET name = ?
                WHERE id = ?
            ''', (category.name, category.id))

            conn.commit()

        return category

    @staticmethod
    def list_categories() -> List[Category]:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            # Get all categories from database
            cursor.execute('SELECT * FROM categories')
            category_rows = cursor.fetchall()

            # Create category objects
            categories = []
            for category_row in category_rows:
                category_id, category_name = category_row
                categories.append(Category(id=category_id, name=category_name))

        return categories
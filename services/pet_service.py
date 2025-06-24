from typing import List, Optional
from fastapi import HTTPException
from generated.models.pet import Pet
from generated.models.category import Category
from generated.models.tag import Tag
from db import db_pool

class PetService:
    @staticmethod
    def create_pet(pet: Pet) -> Pet:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            # Insert or update category if it exists
            if pet.category:
                if pet.category.id is None or pet.category.id == 0:
                    cursor.execute('SELECT MAX(id) FROM categories')
                    max_id_row = cursor.fetchone()
                    category_id = (max_id_row[0] or 0) + 1
                else:
                    category_id = pet.category.id

                cursor.execute('INSERT OR IGNORE INTO categories (id, name) VALUES (?, ?)', (category_id, pet.category.name))
            else:
                category_id = None

            # Generate new ID if not provided
            if pet.id is None or pet.id == 0:
                cursor.execute('SELECT MAX(id) FROM pets')
                max_id_row = cursor.fetchone()
                new_id = (max_id_row[0] or 0) + 1
            else:
                new_id = pet.id

            # Insert pet into database
            photo_urls_str = ','.join(pet.photo_urls) if pet.photo_urls else ''
            cursor.execute('''
                INSERT INTO pets (id, name, category_id, photoUrls, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (new_id, pet.name, category_id, photo_urls_str, pet.status))

            # Insert tags if they exist
            if pet.tags:
                for tag in pet.tags:
                    cursor.execute('INSERT OR IGNORE INTO tags (id, name) VALUES (?, ?)', (tag.id, tag.name))
                    cursor.execute('INSERT INTO pet_tags (pet_id, tag_id) VALUES (?, ?)', (new_id, tag.id))

            conn.commit()

            # Return pet with the generated ID
            pet.id = new_id
        return pet

    @staticmethod
    def update_pet(pet: Pet) -> Pet:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            # Update category if it exists
            if pet.category:
                if pet.category.id is None or pet.category.id == 0:
                    cursor.execute('SELECT MAX(id) FROM categories')
                    max_id_row = cursor.fetchone()
                    category_id = (max_id_row[0] or 0) + 1
                else:
                    category_id = pet.category.id            
                cursor.execute('INSERT OR IGNORE INTO categories (id, name) VALUES (?, ?)', (category_id, pet.category.name))
            else:
                category_id = None

            # Update pet in database
            photo_urls_str = ','.join(pet.photo_urls) if pet.photo_urls else ''
            cursor.execute('''
                UPDATE pets
                SET name = ?, category_id = ?, photoUrls = ?, status = ?
                WHERE id = ?
            ''', (pet.name, category_id, photo_urls_str, pet.status, pet.id))

            # Delete existing tags and insert new ones
            cursor.execute('DELETE FROM pet_tags WHERE pet_id = ?', (pet.id,))
            if pet.tags:
                for tag in pet.tags:
                    cursor.execute('INSERT OR IGNORE INTO tags (id, name) VALUES (?, ?)', (tag.id, tag.name))
                    cursor.execute('INSERT INTO pet_tags (pet_id, tag_id) VALUES (?, ?)', (pet.id, tag.id))

            conn.commit()
        return pet

    @staticmethod
    def find_pets_by_status(status: Optional[str] = "available") -> List[Pet]:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            # Get pets by status
            cursor.execute('SELECT * FROM pets WHERE status = ?', (status,))
            pet_rows = cursor.fetchall()

            # Create pet objects
            pets = []
            for pet_row in pet_rows:
                id, name, category_id, photo_urls_str, status = pet_row
                photo_urls = photo_urls_str.split(',') if photo_urls_str else []

                # Get category if it exists
                category = None
                if category_id:
                    cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
                    category_row = cursor.fetchone()
                    if category_row:
                        category_id, category_name = category_row
                        category = Category(id=category_id, name=category_name)

                # Get tags if they exist
                tags = []
                cursor.execute('SELECT tags.* FROM tags JOIN pet_tags ON tags.id = pet_tags.tag_id WHERE pet_tags.pet_id = ?', (id,))
                tag_rows = cursor.fetchall()
                for tag_row in tag_rows:
                    tag_id, tag_name = tag_row
                    tags.append(Tag(id=tag_id, name=tag_name))

                # Create pet object
                pet = Pet(
                    id=id,
                    name=name,
                    category=category,
                    photo_urls=photo_urls,
                    tags=tags,
                    status=status
                )
                pets.append(pet)
        return pets

    @staticmethod
    def find_pets_by_tags(tags: Optional[str] = None) -> List[Pet]:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            if not tags:
                return []

            # Split comma-separated tags string into a list
            tag_list = [tag.strip() for tag in tags.split(',')]

            # Find pets by tags
            pets = []
            for tag_name in tag_list:
                cursor.execute('''
                    SELECT pets.*
                    FROM pets
                    JOIN pet_tags ON pets.id = pet_tags.pet_id
                    JOIN tags ON pet_tags.tag_id = tags.id
                    WHERE tags.name = ?
                ''', (tag_name,))
                pet_rows = cursor.fetchall()

                for pet_row in pet_rows:
                    id, name, category_id, photo_urls_str, status = pet_row
                    photo_urls = photo_urls_str.split(',') if photo_urls_str else []

                    # Get category if it exists
                    category = None
                    if category_id:
                        cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
                        category_row = cursor.fetchone()
                        if category_row:
                            category_id, category_name = category_row
                            category = Category(id=category_id, name=category_name)

                    # Get tags for this pet
                    tags_list = []
                    cursor.execute('SELECT tags.* FROM tags JOIN pet_tags ON tags.id = pet_tags.tag_id WHERE pet_tags.pet_id = ?', (id,))
                    tag_rows = cursor.fetchall()
                    for tag_row in tag_rows:
                        tag_id, tag_name = tag_row
                        tags_list.append(Tag(id=tag_id, name=tag_name))

                    # Create pet object
                    pet = Pet(
                        id=id,
                        name=name,
                        category=category,
                        photo_urls=photo_urls,
                        tags=tags_list,
                        status=status
                    )
                    pets.append(pet)
        return pets

    @staticmethod
    def get_pet(petId: int) -> Pet:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            # Get pet from database
            cursor.execute('SELECT * FROM pets WHERE id = ?', (petId,))
            pet_row = cursor.fetchone()

            if not pet_row:
                raise HTTPException(status_code=404, detail="Pet not found")

            # Extract pet data
            pet_id, name, category_id, photo_urls_str, status = pet_row
            photo_urls = photo_urls_str.split(',') if photo_urls_str else []

            # Get category if it exists
            category = None
            if category_id:
                cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
                category_row = cursor.fetchone()
                if category_row:
                    category_id, category_name = category_row
                    category = Category(id=category_id, name=category_name)

            # Get tags if they exist
            tags = []
            cursor.execute('SELECT tags.* FROM tags JOIN pet_tags ON tags.id = pet_tags.tag_id WHERE pet_tags.pet_id = ?', (petId,))
            tag_rows = cursor.fetchall()
            for tag_row in tag_rows:
                tag_id, tag_name = tag_row
                tags.append(Tag(id=tag_id, name=tag_name))

            # Create pet object
            pet = Pet(
                id=pet_id,
                name=name,
                category=category,
                photo_urls=photo_urls,
                tags=tags,
                status=status
            )
        return pet

    @staticmethod
    def delete_pet(petId: int) -> dict:
        with db_pool.connection() as conn:
            cursor = conn.cursor()

            # Check if pet exists
            cursor.execute('SELECT * FROM pets WHERE id = ?', (petId,))
            pet_row = cursor.fetchone()

            if not pet_row:
                raise HTTPException(status_code=404, detail="Pet not found")

            # Delete pet and related tags
            cursor.execute('DELETE FROM pet_tags WHERE pet_id = ?', (petId,))
            cursor.execute('DELETE FROM pets WHERE id = ?', (petId,))

            conn.commit()

        return {"message": "Pet deleted"}
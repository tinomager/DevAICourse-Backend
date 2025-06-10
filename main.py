from fastapi import FastAPI, HTTPException
from generated.models.pet import Pet
from generated.models.category import Category
from generated.models.tag import Tag
import sqlite3
import os

app = FastAPI()

@app.get("/pets/{pet_id}", response_model=Pet)
async def get_pet(pet_id: int):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Get pet from database
    cursor.execute('SELECT * FROM pets WHERE id = ?', (pet_id,))
    pet_row = cursor.fetchone()

    if not pet_row:
        conn.close()
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
    cursor.execute('SELECT tags.* FROM tags JOIN pet_tags ON tags.id = pet_tags.tag_id WHERE pet_tags.pet_id = ?', (pet_id,))
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

    conn.close()
    return pet

@app.post("/pets", response_model=Pet)
async def create_pet(pet: Pet):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Insert or update category if it exists
    if pet.category:
        cursor.execute('INSERT OR IGNORE INTO categories (id, name) VALUES (?, ?)', (pet.category.id, pet.category.name))
        category_id = pet.category.id
    else:
        category_id = None

    # Insert pet into database
    photo_urls_str = ','.join(pet.photo_urls) if pet.photo_urls else ''
    cursor.execute('''
        INSERT INTO pets (id, name, category_id, photoUrls, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (pet.id, pet.name, category_id, photo_urls_str, pet.status))

    # Insert tags if they exist
    if pet.tags:
        for tag in pet.tags:
            cursor.execute('INSERT OR IGNORE INTO tags (id, name) VALUES (?, ?)', (tag.id, tag.name))
            cursor.execute('INSERT INTO pet_tags (pet_id, tag_id) VALUES (?, ?)', (pet.id, tag.id))

    conn.commit()
    conn.close()
    return pet

@app.post("/categories", response_model=Category)
async def create_category(category: Category):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Insert category into database
    cursor.execute('INSERT INTO categories (id, name) VALUES (?, ?)',
                   (category.id, category.name))
    conn.commit()
    conn.close()

    return category

@app.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: int):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Get category from database
    cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
    category_row = cursor.fetchone()

    if not category_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found")

    # Extract category data
    category_id, category_name = category_row
    category = Category(id=category_id, name=category_name)

    conn.close()
    return category

@app.get("/tags/{tag_id}", response_model=Tag)
async def get_tag(tag_id: int):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Get tag from database
    cursor.execute('SELECT * FROM tags WHERE id = ?', (tag_id,))
    tag_row = cursor.fetchone()

    if not tag_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Tag not found")

    # Extract tag data
    tag_id, tag_name = tag_row
    tag = Tag(id=tag_id, name=tag_name)

    conn.close()
    return tag

@app.post("/tags", response_model=Tag)
async def create_tag(tag: Tag):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Insert tag into database
    cursor.execute('INSERT INTO tags (id, name) VALUES (?, ?)',
                   (tag.id, tag.name))
    conn.commit()
    conn.close()

    return tag

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
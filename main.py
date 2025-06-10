from fastapi import FastAPI, HTTPException, Query
from generated.models.pet import Pet
from generated.models.category import Category
from generated.models.tag import Tag
from generated.models.order import Order
from generated.models.user import User
from typing import List, Optional
import sqlite3
import os

app = FastAPI()

@app.post("/pet", response_model=Pet, operation_id="addPet")
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

@app.put("/pet", response_model=Pet, operation_id="updatePet")
async def update_pet(pet: Pet):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Update category if it exists
    if pet.category:
        cursor.execute('INSERT OR IGNORE INTO categories (id, name) VALUES (?, ?)', (pet.category.id, pet.category.name))
        category_id = pet.category.id
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
    conn.close()
    return pet

@app.get("/pet/findByStatus", response_model=List[Pet], operation_id="findPetsByStatus")
async def find_pets_by_status(status: Optional[str] = Query("available")):
    conn = sqlite3.connect('data/app.db')
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

    conn.close()
    return pets

@app.get("/pet/findByTags", response_model=List[Pet], operation_id="findPetsByTags")
async def find_pets_by_tags(tags: Optional[str] = Query(None)):
    conn = sqlite3.connect('data/app.db')
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

    conn.close()
    return pets

@app.get("/pet/{petId}", response_model=Pet, operation_id="getPetById")
async def get_pet(petId: int):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Get pet from database
    cursor.execute('SELECT * FROM pets WHERE id = ?', (petId,))
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

    conn.close()
    return pet

@app.delete("/pet/{petId}", response_model=dict, operation_id="deletePet")
async def delete_pet(petId: int):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Check if pet exists
    cursor.execute('SELECT * FROM pets WHERE id = ?', (petId,))
    pet_row = cursor.fetchone()

    if not pet_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pet not found")

    # Delete pet and related tags
    cursor.execute('DELETE FROM pet_tags WHERE pet_id = ?', (petId,))
    cursor.execute('DELETE FROM pets WHERE id = ?', (petId,))

    conn.commit()
    conn.close()
    return {"message": "Pet deleted"}

@app.post("/store/order", response_model=Order, operation_id="placeOrder")
async def place_order(order: Order):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Insert order into database
    cursor.execute('''
        INSERT INTO orders (id, petId, quantity, shipDate, status, complete)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (order.id, order.petId, order.quantity, order.shipDate, order.status, order.complete))

    conn.commit()
    conn.close()
    return order

@app.get("/store/order/{orderId}", response_model=Order, operation_id="getOrderById")
async def get_order(orderId: int):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Get order from database
    cursor.execute('SELECT * FROM orders WHERE id = ?', (orderId,))
    order_row = cursor.fetchone()

    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    # Extract order data
    order_id, petId, quantity, shipDate, status, complete = order_row
    order = Order(
        id=order_id,
        petId=petId,
        quantity=quantity,
        shipDate=shipDate,
        status=status,
        complete=complete
    )

    conn.close()
    return order

@app.delete("/store/order/{orderId}", response_model=dict, operation_id="deleteOrder")
async def delete_order(orderId: int):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Check if order exists
    cursor.execute('SELECT * FROM orders WHERE id = ?', (orderId,))
    order_row = cursor.fetchone()

    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    # Delete order
    cursor.execute('DELETE FROM orders WHERE id = ?', (orderId,))

    conn.commit()
    conn.close()
    return {"message": "Order deleted"}

@app.get("/store/inventory", response_model=dict, operation_id="getInventory")
async def get_inventory():
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Get inventory count by status
    cursor.execute('SELECT status, COUNT(*) FROM pets GROUP BY status')
    inventory_rows = cursor.fetchall()

    inventory = {}
    for status, count in inventory_rows:
        inventory[status] = count

    conn.close()
    return inventory

@app.post("/user", response_model=User, operation_id="createUser")
async def create_user(user: User):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Insert user into database
    cursor.execute('''
        INSERT INTO users (id, username, firstName, lastName, email, password, phone, userStatus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user.id, user.username, user.firstName, user.lastName, user.email, user.password, user.phone, user.userStatus))

    conn.commit()
    conn.close()
    return user

@app.post("/user/createWithList", response_model=List[User], operation_id="createUsersWithListInput")
async def create_users_with_list(users: List[User]):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Insert users into database
    for user in users:
        cursor.execute('''
            INSERT INTO users (id, username, firstName, lastName, email, password, phone, userStatus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user.id, user.username, user.firstName, user.lastName, user.email, user.password, user.phone, user.userStatus))

    conn.commit()
    conn.close()
    return users

@app.get("/user/login", response_model=dict, operation_id="loginUser")
async def login_user(username: Optional[str] = None, password: Optional[str] = None):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Authenticate user
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid username/password")

    # Extract user data
    user_id, username, firstName, lastName, email, password, phone, userStatus = user_row

    conn.close()
    return {"token": "generated-token", "token_type": "bearer"}

@app.get("/user/logout", response_model=dict, operation_id="logoutUser")
async def logout_user():
    # Implement logout logic here
    return {"message": "User logged out"}

@app.get("/user/{username}", response_model=User, operation_id="getUserByName")
async def get_user(username: str):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Get user from database
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Extract user data
    user_id, user_username, firstName, lastName, email, password, phone, userStatus = user_row
    user = User(
        id=user_id,
        username=user_username,
        firstName=firstName,
        lastName=lastName,
        email=email,
        password=password,
        phone=phone,
        userStatus=userStatus
    )

    conn.close()
    return user

@app.put("/user/{username}", response_model=User, operation_id="updateUser")
async def update_user(username: str, user: User):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Update user in database
    cursor.execute('''
        UPDATE users
        SET firstName = ?, lastName = ?, email = ?, password = ?, phone = ?, userStatus = ?
        WHERE username = ?
    ''', (user.firstName, user.lastName, user.email, user.password, user.phone, user.userStatus, username))

    conn.commit()
    conn.close()
    return user

@app.delete("/user/{username}", response_model=dict, operation_id="deleteUser")
async def delete_user(username: str):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))

    conn.commit()
    conn.close()
    return {"message": "User deleted"}

@app.post("/category", response_model=Category, operation_id="addCategory")
async def create_category(category: Category):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Insert category into database
    cursor.execute('INSERT INTO categories (id, name) VALUES (?, ?)',
                   (category.id, category.name))
    conn.commit()
    conn.close()

    return category

@app.put("/category", response_model=Category, operation_id="updateCategory")
async def update_category(category: Category):
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Update category in database
    cursor.execute('''
        UPDATE categories
        SET name = ?
        WHERE id = ?
    ''', (category.name, category.id))

    conn.commit()
    conn.close()
    return category

@app.get("/categories", response_model=List[Category], operation_id="getAllCategories")
async def list_categories():
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()

    # Get all categories from database
    cursor.execute('SELECT * FROM categories')
    category_rows = cursor.fetchall()

    # Create category objects
    categories = []
    for category_row in category_rows:
        category_id, category_name = category_row
        categories.append(Category(id=category_id, name=category_name))

    conn.close()
    return categories

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
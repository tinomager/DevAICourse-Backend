from fastapi import FastAPI, HTTPException, Query
from generated.models.pet import Pet
from generated.models.category import Category
from generated.models.tag import Tag
from generated.models.order import Order
from generated.models.user import User
from typing import List, Optional
import os
from db import db_pool
from services.pet_service import PetService
from services.category_service import CategoryService
from services.user_service import UserService
from services.store_service import StoreService

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/pet", response_model=Pet, operation_id="addPet")
async def create_pet(pet: Pet):
    return PetService.create_pet(pet)

@app.put("/pet", response_model=Pet, operation_id="updatePet")
async def update_pet(pet: Pet):
    return PetService.update_pet(pet)

@app.get("/pet/findByStatus", response_model=List[Pet], operation_id="findPetsByStatus")
async def find_pets_by_status(status: Optional[str] = Query("available")):
    return PetService.find_pets_by_status(status)

@app.get("/pet/findByTags", response_model=List[Pet], operation_id="findPetsByTags")
async def find_pets_by_tags(tags: Optional[str] = Query(None)):
    return PetService.find_pets_by_tags(tags)

@app.get("/pet/{petId}", response_model=Pet, operation_id="getPetById")
async def get_pet(petId: int):
    return PetService.get_pet(petId)

@app.delete("/pet/{petId}", response_model=dict, operation_id="deletePet")
async def delete_pet(petId: int):
    return PetService.delete_pet(petId)

@app.post("/store/order", response_model=Order, operation_id="placeOrder")
async def place_order(order: Order):
    return StoreService.place_order(order)

@app.get("/store/order/{orderId}", response_model=Order, operation_id="getOrderById")
async def get_order(orderId: int):
    return StoreService.get_order(orderId)

@app.delete("/store/order/{orderId}", response_model=dict, operation_id="deleteOrder")
async def delete_order(orderId: int):
    return StoreService.delete_order(orderId)

@app.get("/store/inventory", response_model=dict, operation_id="getInventory")
async def get_inventory():
    return StoreService.get_inventory()

@app.post("/user", response_model=User, operation_id="createUser")
async def create_user(user: User):
    return UserService.create_user(user)

@app.post("/user/createWithList", response_model=List[User], operation_id="createUsersWithListInput")
async def create_users_with_list(users: List[User]):
    return UserService.create_users_with_list(users)

@app.get("/user/login", response_model=dict, operation_id="loginUser")
async def login_user(username: Optional[str] = None, password: Optional[str] = None):
    return UserService.login_user(username, password)

@app.get("/user/logout", response_model=dict, operation_id="logoutUser")
async def logout_user():
    return UserService.logout_user()

@app.get("/user/{username}", response_model=User, operation_id="getUserByName")
async def get_user(username: str):
    return UserService.get_user(username)

@app.put("/user/{username}", response_model=User, operation_id="updateUser")
async def update_user(username: str, user: User):
    return UserService.update_user(username, user)

@app.delete("/user/{username}", response_model=dict, operation_id="deleteUser")
async def delete_user(username: str):
    return UserService.delete_user(username)

@app.post("/category", response_model=Category, operation_id="addCategory")
async def create_category(category: Category):
    return CategoryService.create_category(category)

@app.put("/category", response_model=Category, operation_id="updateCategory")
async def update_category(category: Category):
    return CategoryService.update_category(category)

@app.get("/categories", response_model=List[Category], operation_id="getAllCategories")
async def list_categories():
    return CategoryService.list_categories()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
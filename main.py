from fastapi import FastAPI
from generated.models.pet import Pet
from generated.models.category import Category

app = FastAPI()

@app.get("/pets/{pet_id}", response_model=Pet)
async def get_pet(pet_id: int):
    # Create dummy category
    category = Category(id=1, name="Dog")

    dummy_pet = Pet(
        id=pet_id,
        name="Buddy",
        category=category,
        photoUrls=["https://example.com/pet.jpg"],
        status="available"
    )
    return dummy_pet

@app.post("/pets", response_model=Pet)
async def create_pet(pet: Pet):
    return pet

@app.post("/categories", response_model=Category)
async def create_category(category: Category):
    return category

@app.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: int):
    # Create dummy category
    dummy_category = Category(id=category_id, name="Sample Category")
    return dummy_category

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
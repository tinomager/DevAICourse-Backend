from fastapi import FastAPI
from generated.models.pet import Pet
from generated.models.category import Category
from generated.models.tag import Tag

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

@app.get("/tags/{tag_id}", response_model=Tag)
async def get_tag(tag_id: int):
    dummy_tag = Tag(id=tag_id, name="Sample Tag")
    return dummy_tag

@app.post("/tags", response_model=Tag)
async def create_tag(tag: Tag):
    return tag

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
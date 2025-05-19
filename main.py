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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
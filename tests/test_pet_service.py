import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, MagicMock
from services.pet_service import PetService
from generated.models.pet import Pet
from generated.models.category import Category
from generated.models.tag import Tag
from fastapi import HTTPException

@pytest.fixture
def sample_pet():
    return Pet(
        id=1,
        name="Fluffy",
        category=Category(id=1, name="Cats"),
        photo_urls=["url1", "url2"],
        tags=[Tag(id=1, name="cute")],
        status="available"
    )

def test_create_pet_success(sample_pet):
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        # Simulate DB responses for id generation
        mock_cursor.fetchone.side_effect = [(1,), (1,)]
        result = PetService.create_pet(sample_pet)
        assert result.id == sample_pet.id
        assert result.name == "Fluffy"
        assert result.category.name == "Cats"
        assert result.status == "available"

def test_create_pet_without_category(sample_pet):
    pet = sample_pet.model_copy()
    pet.category = None
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(1,)]
        result = PetService.create_pet(pet)
        assert result.category is None

def test_update_pet_success(sample_pet):
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        result = PetService.update_pet(sample_pet)
        assert result.name == "Fluffy"

def test_get_pet_found(sample_pet):
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        # Simulate pet row, category row, tag rows
        mock_cursor.fetchone.side_effect = [
            (1, "Fluffy", 1, "url1,url2", "available"),  # pet row
            (1, "Cats"),  # category row
        ]
        mock_cursor.fetchall.side_effect = [
            [(1, "cute")],  # tag rows
        ]
        pet = PetService.get_pet(1)
        assert pet.id == 1
        assert pet.name == "Fluffy"
        assert pet.category.name == "Cats"
        assert pet.tags[0].name == "cute"

def test_get_pet_not_found():
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            PetService.get_pet(999)
        assert excinfo.value.status_code == 404

def test_delete_pet_success():
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Fluffy", 1, "url1,url2", "available")
        result = PetService.delete_pet(1)
        assert result["message"] == "Pet deleted"

def test_delete_pet_not_found():
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            PetService.delete_pet(999)
        assert excinfo.value.status_code == 404

def test_find_pets_by_status():
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        # Simulate one pet row
        # 1. First fetchall() for pets
        # 2. fetchone() for category
        # 3. fetchall() for tags
        mock_cursor.fetchall.side_effect = [
            [(1, "Fluffy", 1, "url1,url2", "available")],  # pets
            [(1, "cute")],  # tags for pet
        ]
        mock_cursor.fetchone.side_effect = [
            (1, "Cats"),  # category for pet
        ]
        pets = PetService.find_pets_by_status("available")
        assert len(pets) == 1
        assert pets[0].name == "Fluffy"
        assert pets[0].category.name == "Cats"
        assert pets[0].tags[0].name == "cute"

def test_find_pets_by_tags():
    with patch("services.pet_service.db_pool") as mock_db_pool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        # Simulate one pet row
        # 1. fetchall() for pets with tag
        # 2. fetchone() for category
        # 3. fetchall() for tags for this pet
        mock_cursor.fetchall.side_effect = [
            [(1, "Fluffy", 1, "url1,url2", "available")],  # pets with tag
            [(1, "cute")],  # tags for pet
        ]
        mock_cursor.fetchone.side_effect = [
            (1, "Cats"),  # category for pet
        ]
        pets = PetService.find_pets_by_tags("cute")
        assert len(pets) == 1
        assert pets[0].name == "Fluffy"
        assert pets[0].category.name == "Cats"
        assert pets[0].tags[0].name == "cute"
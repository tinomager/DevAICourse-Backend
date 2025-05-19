# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.pet_api_base import BasePetApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictBytes, StrictInt, StrictStr, field_validator
from typing import Any, List, Optional, Tuple, Union
from typing_extensions import Annotated
from openapi_server.models.api_response import ApiResponse
from openapi_server.models.pet import Pet
from openapi_server.security_api import get_token_petstore_auth, get_token_api_key

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/pet",
    responses={
        200: {"model": Pet, "description": "Successful operation"},
        400: {"description": "Invalid input"},
        422: {"description": "Validation exception"},
        200: {"description": "Unexpected error"},
    },
    tags=["pet"],
    summary="Add a new pet to the store.",
    response_model_by_alias=True,
)
async def add_pet(
    pet: Annotated[Pet, Field(description="Create a new pet in the store")] = Body(None, description="Create a new pet in the store"),
    token_petstore_auth: TokenModel = Security(
        get_token_petstore_auth, scopes=["write:pets", "read:pets"]
    ),
) -> Pet:
    """Add a new pet to the store."""
    if not BasePetApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePetApi.subclasses[0]().add_pet(pet)


@router.delete(
    "/pet/{petId}",
    responses={
        200: {"description": "Pet deleted"},
        400: {"description": "Invalid pet value"},
        200: {"description": "Unexpected error"},
    },
    tags=["pet"],
    summary="Deletes a pet.",
    response_model_by_alias=True,
)
async def delete_pet(
    petId: Annotated[StrictInt, Field(description="Pet id to delete")] = Path(..., description="Pet id to delete"),
    api_key: Optional[StrictStr] = Header(None, description=""),
    token_petstore_auth: TokenModel = Security(
        get_token_petstore_auth, scopes=["write:pets", "read:pets"]
    ),
) -> None:
    """Delete a pet."""
    if not BasePetApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePetApi.subclasses[0]().delete_pet(petId, api_key)


@router.get(
    "/pet/findByStatus",
    responses={
        200: {"model": List[Pet], "description": "successful operation"},
        400: {"description": "Invalid status value"},
        200: {"description": "Unexpected error"},
    },
    tags=["pet"],
    summary="Finds Pets by status.",
    response_model_by_alias=True,
)
async def find_pets_by_status(
    status: Annotated[Optional[StrictStr], Field(description="Status values that need to be considered for filter")] = Query(available, description="Status values that need to be considered for filter", alias="status"),
    token_petstore_auth: TokenModel = Security(
        get_token_petstore_auth, scopes=["write:pets", "read:pets"]
    ),
) -> List[Pet]:
    """Multiple status values can be provided with comma separated strings."""
    if not BasePetApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePetApi.subclasses[0]().find_pets_by_status(status)


@router.get(
    "/pet/findByTags",
    responses={
        200: {"model": List[Pet], "description": "successful operation"},
        400: {"description": "Invalid tag value"},
        200: {"description": "Unexpected error"},
    },
    tags=["pet"],
    summary="Finds Pets by tags.",
    response_model_by_alias=True,
)
async def find_pets_by_tags(
    tags: Annotated[Optional[List[StrictStr]], Field(description="Tags to filter by")] = Query(None, description="Tags to filter by", alias="tags"),
    token_petstore_auth: TokenModel = Security(
        get_token_petstore_auth, scopes=["write:pets", "read:pets"]
    ),
) -> List[Pet]:
    """Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing."""
    if not BasePetApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePetApi.subclasses[0]().find_pets_by_tags(tags)


@router.get(
    "/pet/{petId}",
    responses={
        200: {"model": Pet, "description": "successful operation"},
        400: {"description": "Invalid ID supplied"},
        404: {"description": "Pet not found"},
        200: {"description": "Unexpected error"},
    },
    tags=["pet"],
    summary="Find pet by ID.",
    response_model_by_alias=True,
)
async def get_pet_by_id(
    petId: Annotated[StrictInt, Field(description="ID of pet to return")] = Path(..., description="ID of pet to return"),
    token_petstore_auth: TokenModel = Security(
        get_token_petstore_auth, scopes=["write:pets", "read:pets"]
    ),
    token_api_key: TokenModel = Security(
        get_token_api_key
    ),
) -> Pet:
    """Returns a single pet."""
    if not BasePetApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePetApi.subclasses[0]().get_pet_by_id(petId)


@router.put(
    "/pet",
    responses={
        200: {"model": Pet, "description": "Successful operation"},
        400: {"description": "Invalid ID supplied"},
        404: {"description": "Pet not found"},
        422: {"description": "Validation exception"},
        200: {"description": "Unexpected error"},
    },
    tags=["pet"],
    summary="Update an existing pet.",
    response_model_by_alias=True,
)
async def update_pet(
    pet: Annotated[Pet, Field(description="Update an existent pet in the store")] = Body(None, description="Update an existent pet in the store"),
    token_petstore_auth: TokenModel = Security(
        get_token_petstore_auth, scopes=["write:pets", "read:pets"]
    ),
) -> Pet:
    """Update an existing pet by Id."""
    if not BasePetApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePetApi.subclasses[0]().update_pet(pet)


@router.post(
    "/pet/{petId}",
    responses={
        200: {"model": Pet, "description": "successful operation"},
        400: {"description": "Invalid input"},
        200: {"description": "Unexpected error"},
    },
    tags=["pet"],
    summary="Updates a pet in the store with form data.",
    response_model_by_alias=True,
)
async def update_pet_with_form(
    petId: Annotated[StrictInt, Field(description="ID of pet that needs to be updated")] = Path(..., description="ID of pet that needs to be updated"),
    name: Annotated[Optional[StrictStr], Field(description="Name of pet that needs to be updated")] = Query(None, description="Name of pet that needs to be updated", alias="name"),
    status: Annotated[Optional[StrictStr], Field(description="Status of pet that needs to be updated")] = Query(None, description="Status of pet that needs to be updated", alias="status"),
    token_petstore_auth: TokenModel = Security(
        get_token_petstore_auth, scopes=["write:pets", "read:pets"]
    ),
) -> Pet:
    """Updates a pet resource based on the form data."""
    if not BasePetApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePetApi.subclasses[0]().update_pet_with_form(petId, name, status)


@router.post(
    "/pet/{petId}/uploadImage",
    responses={
        200: {"model": ApiResponse, "description": "successful operation"},
        400: {"description": "No file uploaded"},
        404: {"description": "Pet not found"},
        200: {"description": "Unexpected error"},
    },
    tags=["pet"],
    summary="Uploads an image.",
    response_model_by_alias=True,
)
async def upload_file(
    petId: Annotated[StrictInt, Field(description="ID of pet to update")] = Path(..., description="ID of pet to update"),
    additional_metadata: Annotated[Optional[StrictStr], Field(description="Additional Metadata")] = Query(None, description="Additional Metadata", alias="additionalMetadata"),
    body: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]] = Body(None, description=""),
    token_petstore_auth: TokenModel = Security(
        get_token_petstore_auth, scopes=["write:pets", "read:pets"]
    ),
) -> ApiResponse:
    """Upload image of the pet."""
    if not BasePetApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePetApi.subclasses[0]().upload_file(petId, additional_metadata, body)

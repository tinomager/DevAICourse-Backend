# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.user import User


class BaseUserApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseUserApi.subclasses = BaseUserApi.subclasses + (cls,)
    async def create_user(
        self,
        user: Annotated[Optional[User], Field(description="Created user object")],
    ) -> User:
        """This can only be done by the logged in user."""
        ...


    async def create_users_with_list_input(
        self,
        user: Optional[List[User]],
    ) -> User:
        """Creates list of users with given input array."""
        ...


    async def delete_user(
        self,
        username: Annotated[StrictStr, Field(description="The name that needs to be deleted")],
    ) -> None:
        """This can only be done by the logged in user."""
        ...


    async def get_user_by_name(
        self,
        username: Annotated[StrictStr, Field(description="The name that needs to be fetched. Use user1 for testing")],
    ) -> User:
        """Get user detail based on username."""
        ...


    async def login_user(
        self,
        username: Annotated[Optional[StrictStr], Field(description="The user name for login")],
        password: Annotated[Optional[StrictStr], Field(description="The password for login in clear text")],
    ) -> str:
        """Log into the system."""
        ...


    async def logout_user(
        self,
    ) -> None:
        """Log user out of the system."""
        ...


    async def update_user(
        self,
        username: Annotated[StrictStr, Field(description="name that need to be deleted")],
        user: Annotated[Optional[User], Field(description="Update an existent user in the store")],
    ) -> None:
        """This can only be done by the logged in user."""
        ...

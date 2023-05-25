"""User information models module."""
from datetime import datetime
from typing import Callable, ClassVar, Optional, Union
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import Base


class UserBase(SQLModel):
    """User base model with shared attributes."""

    first_name: str = Field(max_length=200, nullable=False)
    last_name: str = Field(max_length=200, nullable=False)
    username: str = Field(max_length=100, unique=True, index=True, nullable=False)
    email: str = Field(max_length=100, unique=True, index=True, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
    is_staff: bool = Field(default=False, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    last_login: Optional[datetime] = Field(nullable=True)


class UserCreate(UserBase):
    """User create model."""

    password: str = Field(max_length=500, nullable=False)
    created_by: UUID
    modified_by: UUID


class UserUpdate(SQLModel):
    """User update model."""

    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    password: Optional[str]
    email: Optional[str]
    is_superuser: Optional[bool]
    is_staff: Optional[bool]
    is_active: Optional[bool]
    last_login: Optional[datetime]
    modified_by: UUID


class UserDB(Base, UserBase, table=True):
    """User model for database table."""

    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "auth_user"
    hashed_password: str = Field(max_length=500, nullable=False)


class UserRead(UserBase):
    """User read one model."""

    uid: UUID
    date_created: datetime
    date_modified: datetime
    last_login: Optional[datetime]
    created_by: UUID
    modified_by: UUID


class UserReadMany(SQLModel):
    """User read many model."""

    count: int
    result: list[UserRead]

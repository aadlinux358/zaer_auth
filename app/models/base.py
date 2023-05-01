"""Module that contains Base model that holds shared attributes."""
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, func, text


class TimestampModel(SQLModel):
    """Model that defines timestamp attributes."""

    date_created: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": func.now()},
    )

    date_modified: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )


class Base(TimestampModel):
    """Base model with attributes shared among all models."""

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "unique": True,
        },
    )
    created_by: uuid.UUID = Field(nullable=False)
    modified_by: uuid.UUID = Field(nullable=False)

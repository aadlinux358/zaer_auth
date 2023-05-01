"""Database engine and session creation module."""
from collections.abc import AsyncGenerator
from sys import modules

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.settings import settings

db_connection_str = settings.async_db_connection_string
if "pytest" in modules:
    db_connection_str = settings.async_test_db_connection_string


async_engine = create_async_engine(db_connection_str, echo=False, future=True)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide async session."""
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

"""Database engine and session creation module."""
from collections.abc import AsyncGenerator
from operator import attrgetter
from sys import modules

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.settings import settings

user, password, db, host, port, test_db, test_port = attrgetter(
    "pg_user",
    "pg_password",
    "pg_db",
    "pg_server",
    "pg_port",
    "pg_test_db",
    "pg_test_port",
)(settings)
db_connection_str = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
if "pytest" in modules:
    db_connection_str = (
        f"postgresql+asyncpg://{user}:{password}@{host}:{test_port}/{test_db}"
    )


async_engine = create_async_engine(db_connection_str, echo=False, future=True)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide async session."""
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

"""Pytest configuration module."""
import asyncio
from typing import AsyncGenerator, Final, Generator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# for models to be detected before calling metadata.create_all
from app import models  # noqa: F401
from app.core.db import async_engine
from app.core.settings import settings
from app.main import app

TEST_URL: Final = f"http://{settings.api_v1_prefix}"


def event_loop(request) -> Generator:  # noqa: indirect usage
    """Get the event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture that provide async session."""
    async with AsyncClient(app=app, base_url=TEST_URL) as client:
        yield client


@pytest_asyncio.fixture(scope="function", autouse=True)
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture that provide async session."""
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()

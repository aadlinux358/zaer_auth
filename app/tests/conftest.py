"""Pytest configuration module."""
import asyncio
import uuid
from typing import AsyncGenerator, Final, Generator

import pytest_asyncio
from fastapi_jwt_auth import AuthJWT  # type: ignore
from httpx import AsyncClient, Headers
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_engine
from app.core.settings import settings
from app.main import app

# for models to be detected before calling metadata.create_all
from app.models import UserDB
from app.security import password

TEST_URL: Final = f"http://{settings.api_v1_prefix}"


def event_loop(request) -> Generator:  # noqa: indirect usage
    """Get the event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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


@pytest_asyncio.fixture(scope="function")
async def user(session: AsyncSession) -> UserDB:
    """Create test user."""
    hashed_password = password.get_password_hash("password")
    user = UserDB(
        first_name="hosanna",
        last_name="abel",
        email="hosi1@zaer.com",
        username="hosi",
        hashed_password=hashed_password,
        is_superuser=True,
        is_active=True,
        is_staff=True,
        last_login=None,
        created_by=uuid.uuid4(),
        modified_by=uuid.uuid4(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def headers(user: UserDB) -> Headers:
    """Create test client headers."""
    access_token = AuthJWT().create_access_token(subject=str(user.uid))
    headers = Headers({"Authorization": f"Bearer {access_token}"})
    return headers


@pytest_asyncio.fixture(scope="function")
async def client(headers: Headers) -> AsyncGenerator[AsyncClient, None]:
    """Fixture that provide async session."""
    async with AsyncClient(app=app, base_url=TEST_URL) as client:
        client.headers = headers
        yield client

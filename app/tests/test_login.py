"""User loging tests module."""
import uuid
from typing import Final

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import UserDB
from app.security import password

ENDPOINT: Final = "login"
USER_ID: Final = "38eb651b-bd33-4f9a-beb2-0f9d52d7acc6"


@pytest.mark.asyncio
async def test_login(client: AsyncClient, session: AsyncSession):
    pwd_hash = password.get_password_hash("hailepassword")
    user = UserDB(
        first_name="haile",
        last_name="marikos",
        username="haile123",
        hashed_password=pwd_hash,
        email="haile123@zaer.com",
        created_by=uuid.UUID(USER_ID),
        modified_by=uuid.UUID(USER_ID),
        last_login=None,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    payload = dict(username="haile123", password="hailepassword")
    response = await client.post(f"{ENDPOINT}", json=payload)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["access_token"]
    assert response.json()["user"]["username"] == "haile123"
    assert response.json()["user"]["last_login"]


@pytest.mark.asyncio
async def test_invalid_username(client: AsyncClient, session: AsyncSession):
    pwd_hash = password.get_password_hash("hailepassword")
    user = UserDB(
        first_name="haile",
        last_name="marikos",
        username="haile123",
        hashed_password=pwd_hash,
        email="haile123@zaer.com",
        created_by=uuid.UUID(USER_ID),
        modified_by=uuid.UUID(USER_ID),
        last_login=None,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    payload = dict(username="haile", password="hailepassword")
    response = await client.post(f"{ENDPOINT}", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json()["detail"] == "invalid username or password."


@pytest.mark.asyncio
async def test_invalid_password(client: AsyncClient, session: AsyncSession):
    pwd_hash = password.get_password_hash("hailepassword")
    user = UserDB(
        first_name="haile",
        last_name="marikos",
        username="haile123",
        hashed_password=pwd_hash,
        email="haile123@zaer.com",
        created_by=uuid.UUID(USER_ID),
        modified_by=uuid.UUID(USER_ID),
        last_login=None,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    payload = dict(username="haile123", password="password")
    response = await client.post(f"{ENDPOINT}", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json()["detail"] == "invalid username or password."

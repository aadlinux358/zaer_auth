"""User api tests module."""
import copy
import uuid
from typing import Final

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserDB
from app.security import password

ENDPOINT: Final = "users"
USER_ID: Final = "38eb651b-bd33-4f9a-beb2-0f9d52d7acc6"
USER_TEST_DATA: Final = {
    "first_name": "Semere",
    "last_name": "Tewelde",
    "username": "user1",
    "password": "password",
    "email": "user1@zaer.com",
    "created_by": USER_ID,
    "modified_by": USER_ID,
}


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, session: AsyncSession):
    payload = copy.deepcopy(USER_TEST_DATA)

    response = await client.post(f"/{ENDPOINT}", json=payload)

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    response_json = response.json()
    for k, v in USER_TEST_DATA.items():
        if k == "password":
            pwd = password.get_password_hash(v)
            assert password.verify_password(v, pwd)
            continue
        if isinstance(v, str):
            v = v.lower().strip()
        assert response_json[k] == v


@pytest.mark.asyncio
async def test_duplicate_violation(client: AsyncClient, session: AsyncSession):
    hashed_password = password.get_password_hash("password")
    user = UserDB(
        first_name="kbrom",
        last_name="temesgen",
        email="user1@zaer.com",
        username="user1",
        hashed_password=hashed_password,
        last_login=None,
        created_by=uuid.UUID(USER_ID),
        modified_by=uuid.UUID(USER_ID),
    )
    session.add(user)
    await session.commit()

    payload = copy.deepcopy(USER_TEST_DATA)
    response = await client.post(f"/{ENDPOINT}", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert (
        response.json()["detail"]
        == "integrity error. eg. duplicate field or invalid field value."
    )


@pytest.mark.asyncio
async def test_get_users_list(client: AsyncClient, session: AsyncSession):
    hashed_password = password.get_password_hash("password")
    users = [
        UserDB(
            first_name="kbrom",
            last_name="temesgen",
            email="user1@zaer.com",
            username="user1",
            hashed_password=hashed_password,
            last_login=None,
            created_by=uuid.UUID(USER_ID),
            modified_by=uuid.UUID(USER_ID),
        ),
        UserDB(
            first_name="senait",
            last_name="amlesom",
            email="user2@zaer.com",
            username="user2",
            hashed_password=hashed_password,
            last_login=None,
            created_by=uuid.UUID(USER_ID),
            modified_by=uuid.UUID(USER_ID),
        ),
        UserDB(
            first_name="yemane",
            last_name="medhanie",
            email="user3@zaer.com",
            username="user3",
            hashed_password=hashed_password,
            last_login=None,
            created_by=uuid.UUID(USER_ID),
            modified_by=uuid.UUID(USER_ID),
        ),
    ]
    for user in users:
        session.add(user)
    await session.commit()

    response = await client.get(f"{ENDPOINT}")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["count"] == 3
    assert len(response.json()["result"]) == 3
    assert isinstance(response.json()["result"], list)


@pytest.mark.asyncio
async def test_get_user_by_uid(client: AsyncClient, session: AsyncSession):
    hashed_password = password.get_password_hash("password")
    user = UserDB(
        first_name="yemane",
        last_name="medhanie",
        email="user3@zaer.com",
        username="user3",
        hashed_password=hashed_password,
        last_login=None,
        created_by=uuid.UUID(USER_ID),
        modified_by=uuid.UUID(USER_ID),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    response = await client.get(f"{ENDPOINT}/{user.uid}")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["uid"] == str(user.uid)


@pytest.mark.asyncio
async def test_user_not_found(client: AsyncClient, session: AsyncSession):
    response = await client.get(f"{ENDPOINT}/{uuid.uuid4()}")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json()["detail"] == "user not found."


@pytest.mark.asyncio
async def test_can_update_user(client: AsyncClient, session: AsyncSession):
    hashed_password = password.get_password_hash("password")
    user = UserDB(
        first_name="yemane",
        last_name="medhanie",
        email="user3@zaer.com",
        username="user3",
        hashed_password=hashed_password,
        last_login=None,
        created_by=uuid.UUID(USER_ID),
        modified_by=uuid.UUID(USER_ID),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    payload = dict(
        first_name="YONATAN",
        last_name="ALEX",
        email="newuser@zaer.com",
        username="xavier",
        password="newpassword",
        is_superuser=True,
        modified_by=USER_ID,
    )

    response = await client.patch(f"{ENDPOINT}/{user.uid}", json=payload)
    await session.refresh(user)
    password.get_password_hash("newpassword")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["first_name"] == "yonatan"
    assert response.json()["last_name"] == "alex"
    assert response.json()["email"] == "newuser@zaer.com"
    assert response.json()["is_superuser"]
    assert password.verify_password("newpassword", user.hashed_password)

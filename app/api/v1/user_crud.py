"""User crud operations module."""
from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import UserCreate, UserDB, UserReadMany, UserUpdate
from app.security import password


class UserCRUD:
    """Class defining all database related operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Database operations class initializer."""
        self.session = session

    async def create_user(self, payload: UserCreate) -> UserDB:
        """Create user in the database."""
        values = payload.dict()
        hashed_password = password.get_password_hash(values["password"])
        values["hashed_password"] = hashed_password
        values["first_name"] = values["first_name"].strip().lower()
        values["last_name"] = values["last_name"].strip().lower()

        user = UserDB(**values)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def read_many(self) -> UserReadMany:
        """Read many user records."""
        statement = select(UserDB)
        result = await self.session.exec(statement)  # type: ignore

        return UserReadMany(count=len(result.all()), result=result.all())

    async def read_by_uid(self, user_uid: UUID) -> Optional[UserDB]:
        """Read user by uid."""
        statement = select(UserDB).where(UserDB.uid == user_uid)
        result = await self.session.exec(statement)  # type: ignore
        user = result.one_or_none()

        return user

    async def read_by_username(self, username: str) -> Optional[UserDB]:
        """Read user by username."""
        statement = select(UserDB).where(UserDB.username == username)
        result = await self.session.exec(statement)  # type: ignore
        user = result.one_or_none()
        return user

    async def update_user(
        self, user_uid: UUID, payload: UserUpdate
    ) -> Optional[UserDB]:
        """Update user."""
        user = await self.read_by_uid(user_uid)
        if user is None:
            return None

        values = payload.dict(exclude_unset=True)
        values["hashed_password"] = password.get_password_hash(values["password"])
        values["first_name"] = values["first_name"].strip().lower()
        values["last_name"] = values["last_name"].strip().lower()
        values.pop("password")
        for k, v in values.items():
            setattr(user, k, v)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def delete_user(self, user_uid: UUID) -> bool:
        """
        Delete user.

        Note that this method does not remove the user from
        the database, instead it marks it as inactive.
        """
        user = await self.read_by_uid(user_uid)
        if user is None:
            return False
        setattr(user, "is_active", False)

        self.session.add(user)
        await self.session.commit()

        return True

"""User information api dependencies module."""
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.user_crud import UserCRUD
from app.core.db import get_async_session


async def get_user_crud(
    session: AsyncSession = Depends(get_async_session),
) -> UserCRUD:
    """Dependency function that initialize user crud operations class."""
    return UserCRUD(session=session)

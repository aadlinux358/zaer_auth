"""User api endpoints module."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.v1.dependencies import get_user_crud
from app.api.v1.user_crud import UserCRUD
from app.models.user import UserCreate, UserRead, UserReadMany, UserUpdate

router = APIRouter(prefix="/users", tags=["user"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, users: UserCRUD = Depends(get_user_crud)):
    """Create User."""
    try:
        user = await users.create_user(payload)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="integrity error. eg. duplicate field or invalid field value.",
        )
    return user


@router.get("", response_model=UserReadMany)
async def read_many(users: UserCRUD = Depends(get_user_crud)):
    """Read many users."""
    user_list = await users.read_many()

    return user_list


@router.get("/{user_uid}", response_model=UserRead)
async def read_by_uid(user_uid: UUID, users: UserCRUD = Depends(get_user_crud)):
    """Read user by uid."""
    user = await users.read_by_uid(user_uid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found."
        )
    return user


@router.patch("/{user_uid}", response_model=UserRead)
async def update_user(
    user_uid: UUID,
    payload: UserUpdate,
    users: UserCRUD = Depends(get_user_crud),
):
    """Update user."""
    if payload.first_name:
        payload.first_name.strip().lower()
    if payload.last_name:
        payload.last_name.strip().lower()
    user = await users.update_user(user_uid, payload)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found."
        )
    return user

"""User api endpoints module."""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT  # type: ignore
from sqlalchemy.exc import IntegrityError

from app.api.v1.dependencies import get_user_crud
from app.api.v1.user_crud import UserCRUD
from app.models.user import UserCreate, UserRead, UserReadMany, UserUpdate

router = APIRouter(prefix="/users", tags=["user"])

UserCRUDDep = Annotated[UserCRUD, Depends(get_user_crud)]
AuthJWTDep = Annotated[AuthJWT, Depends()]


async def superuser_or_error(user_claims: Optional[dict]) -> None:
    """Check if user is superuser."""
    if user_claims is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid token"
        )

    if not user_claims.get('is_superuser'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="no sufficient privileges."
        )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, users: UserCRUDDep, Authorize: AuthJWTDep):
    """Create User."""
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    await superuser_or_error(user_claims)
    try:
        user = await users.create_user(payload)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="integrity error. eg. duplicate field or invalid field value.",
        )
    return user


@router.get("", response_model=UserReadMany)
async def read_many(users: UserCRUDDep, Authorize: AuthJWTDep):
    """Read many users."""
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    await superuser_or_error(user_claims)
    user_list = await users.read_many()
    return user_list


@router.get("/{user_uid}", response_model=UserRead)
async def read_by_uid(user_uid: UUID, users: UserCRUDDep, Authorize: AuthJWTDep):
    """Read user by uid."""
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    await superuser_or_error(user_claims)
    user = await users.read_by_uid(user_uid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found."
        )
    return user


@router.patch("/{user_uid}", response_model=UserRead)
async def update_user(
    user_uid: UUID, payload: UserUpdate, users: UserCRUDDep, Authorize: AuthJWTDep
):
    """Update user."""
    Authorize.jwt_required()
    user_claims = Authorize.get_raw_jwt()
    await superuser_or_error(user_claims)

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

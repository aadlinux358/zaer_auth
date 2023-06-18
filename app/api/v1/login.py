"""User login api module."""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT  # type: ignore
from pydantic import BaseModel

from app.api.v1.dependencies import get_user_crud
from app.api.v1.user_crud import UserCRUD
from app.models.user import UserRead, UserUpdate
from app.security import password

router = APIRouter(prefix="/login", tags=["login"])

UserCRUDDep = Annotated[UserCRUD, Depends(get_user_crud)]


class LoginCredential(BaseModel):
    """Users login credentials model."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str
    user: UserRead


@router.post("", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def login(
    credentials: LoginCredential,
    users: UserCRUDDep,
    Authorize: AuthJWT = Depends(),
) -> LoginResponse:
    """Login user."""
    user = await users.read_by_username(credentials.username)
    if not (
        user and password.verify_password(credentials.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid username or password.",
        )
    if user and user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="inactive user."
        )
    user = await users.update_user(
        user.uid, payload=UserUpdate(last_login=datetime.now(), modified_by=user.uid)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found."
        )

    user_claims = {
        "is_superuser": user.is_superuser,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
    }
    access_token = Authorize.create_access_token(
        subject=str(user.uid), user_claims=user_claims
    )
    return LoginResponse(access_token=access_token, user=UserRead(**user.dict()))

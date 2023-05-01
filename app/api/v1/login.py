"""User login api module."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT  # type: ignore
from pydantic import BaseModel

from app.api.v1.dependencies import get_user_crud
from app.api.v1.user_crud import UserCRUD
from app.security import password

router = APIRouter(prefix="/login", tags=["login"])


class LoginCredential(BaseModel):
    """Users login credentials model."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str


@router.post("", response_model=LoginResponse)
async def login(
    credentials: LoginCredential,
    Authorize: AuthJWT = Depends(),
    users: UserCRUD = Depends(get_user_crud),
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

    access_token = Authorize.create_access_token(subject=str(user.uid))
    return LoginResponse(access_token=access_token)

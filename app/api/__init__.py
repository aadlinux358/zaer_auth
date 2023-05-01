"""Auth app api package."""
from fastapi import APIRouter

from app.api.v1.login import router as login_router
from app.api.v1.public_key import router as public_key_router
from app.api.v1.user import router as user_router

api_router = APIRouter()

api_router.include_router(user_router)
api_router.include_router(login_router)
api_router.include_router(public_key_router)

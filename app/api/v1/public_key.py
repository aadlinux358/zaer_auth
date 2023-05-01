"""Public key serving endpoint module."""
from fastapi import APIRouter

from app.core.settings import settings

router = APIRouter(prefix="/public-key", tags=["public_key"])


@router.get("")
async def get_public_key():
    """Serve public key."""
    return {"public_key": settings.authjwt_public_key}

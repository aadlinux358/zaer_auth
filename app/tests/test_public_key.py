"""Public key test module."""
from typing import Final

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.settings import settings

ENDPOINT: Final = "public-key"


@pytest.mark.asyncio
async def test_get_public_key(client: AsyncClient):
    response = await client.get(f"{ENDPOINT}")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["public_key"] == settings.authjwt_public_key

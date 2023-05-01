"""FastAPI application entry point module."""
from typing import Final

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT  # type: ignore
from fastapi_jwt_auth.exceptions import AuthJWTException  # type: ignore

from app.api import api_router
from app.core.settings import settings
from app.models.health_check import HealthCheck

origins: Final = ["*"]

app = FastAPI(description="ZaEr Authentication App")


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check() -> HealthCheck:
    """Get service status."""
    return HealthCheck(
        name=settings.app_name,
        version=settings.version,
        description=settings.description,
    )


# callback to get your configuration
@AuthJWT.load_config
def get_config():
    """Get application pydantic settings configuration."""
    return settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    """Handle jwt authentication errors and send json response."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(api_router, prefix=settings.api_v1_prefix)

"""ZaEr auth app health status."""
from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Model for service status information."""

    name: str
    version: str
    description: str

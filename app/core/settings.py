"""Auth service application settings module."""
from urllib.parse import quote_plus

from pydantic import BaseSettings, validator

from app.security import keys


class Settings(BaseSettings):
    """Settings configuration class."""

    # Base
    api_v1_prefix: str
    app_name: str
    debug: bool
    version: str
    description: str

    # Database
    pg_user: str
    pg_password: str
    pg_server: str
    pg_db: str
    pg_port: int
    pg_test_db: str
    pg_test_port: int

    # auth
    pem_key_file_path: str
    pem_key_file_password: bytes
    authjwt_access_token_expires = False
    # authjwt_token_location: set = {"cookies"}
    authjwt_token_location: set = {"headers"}
    # authjwt_cookie_samesite: str ='none'
    # authjwt_cookie_secure: bool = True
    # authjwt_cookie_domain='localhost'
    # authjwt_cookie_csrf_protect=False
    authjwt_public_key: str = keys.get_assymetric_key(key="public")  # type: ignore
    authjwt_private_key: str = keys.get_assymetric_key(key="private")  # type: ignore
    authjwt_algorithm: str

    @validator("pg_user", "pg_password", "pg_server", "pg_db", "pg_test_db")
    def url_encode(cls, v):
        """Url quote strings."""
        v = quote_plus(v)
        return v

    class Config:
        """Further settings customization config class."""

        env_file = ".env"


settings = Settings()

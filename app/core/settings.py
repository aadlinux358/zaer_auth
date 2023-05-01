"""Auth service application settings module."""
from typing import Union

from pydantic import BaseSettings, PostgresDsn

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
    async_db_connection_string: Union[PostgresDsn, str]
    async_test_db_connection_string: Union[PostgresDsn, str]
    pg_user: str
    pg_password: str
    pg_server: str
    pg_db: str

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

    class Config:
        """Further settings customization config class."""

        env_file = ".env"


settings = Settings()

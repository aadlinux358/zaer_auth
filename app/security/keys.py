"""Auth app assymetric keys module."""
import os

from cryptography.hazmat.backends import default_backend  # type: ignore
from cryptography.hazmat.primitives import serialization  # type: ignore
from dotenv import load_dotenv

load_dotenv()
file_path: str = os.environ["pem_key_file_path"]
password: bytes = bytes(os.environ["pem_key_file_password"], encoding="utf-8")
# file_path:str = '/app/private.pem'
# password: bytes = b'zaer@2022'


def get_assymetric_key(key: str) -> bytes:
    """Get assymetric key."""
    keys: dict[str, bytes] = {}
    with open(file_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            data=key_file.read(), password=password, backend=default_backend()
        )
    public_key = private_key.public_key()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1
    )
    keys["private"] = private_bytes
    keys["public"] = public_bytes

    return keys[key]

"""Create superuser module."""
import asyncio
import sys
import uuid
from getpass import getpass as getpass
from urllib.parse import quote_plus as qp

import asyncpg
from pydantic import BaseModel, EmailStr, Field

from app.security import password as pwd


class SuperuserCreate(BaseModel):
    """Auth user model."""

    uid: uuid.UUID
    first_name: str = Field(max_length=200)
    last_name: str = Field(max_length=200)
    username: str = Field(max_length=100)
    email: EmailStr
    password: str = Field(max_length=500)
    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=True)
    is_active: bool = Field(default=True)
    created_by: uuid.UUID
    modified_by: uuid.UUID


class ConnectionString(BaseModel):
    """Database connection model."""

    username: str
    password: str
    hostname: str
    port: int
    db: str


async def main(user: SuperuserCreate, conn_str: ConnectionString):
    """Create superuser.."""
    # Establish a connection to an existing database named "test"
    # as a "postgres" user.
    conn = await asyncpg.connect(
        f"postgresql://"
        f"{qp(conn_str.username)}:{qp(conn_str.password)}"
        f"@{qp(conn_str.hostname)}:{conn_str.port}/{qp(conn_str.db)}"
    )

    # Insert a record into auth_user table.
    await conn.execute(
        """
        INSERT INTO auth_user(uid, first_name, last_name,
                              username, email, hashed_password,
                              is_superuser, is_staff, is_active,
                              created_by, modified_by)
                              VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    """,
        user.uid,
        user.first_name,
        user.last_name,
        user.username,
        user.email,
        user.password,
        user.is_superuser,
        user.is_staff,
        user.is_active,
        user.created_by,
        user.modified_by,
    )

    await conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(f"\nUsage: python {sys.argv[0]} db_user db_name hostname port")
        sys.exit(1)
    db_password = getpass(f"password for database user [{sys.argv[1]}]: ")
    conn_str = ConnectionString(
        username=sys.argv[1],
        password=db_password,
        db=sys.argv[2],
        hostname=sys.argv[3],
        port=int(sys.argv[4]),
    )
    print("\n\tCreate Superuser\n")
    first_name = input(">>> Enter superuser's first name: ")
    last_name = input(">>> Enter superuser's last name: ")
    email = input(">>> Enter superuser's email: ")
    username = input(">>> Enter superuser's username: ")
    password = getpass(">>> Enter superuser's password: ")
    confirm_pass = getpass(">>> Confirm superuser's password: ")

    if password != confirm_pass:
        print("ERROR: passwords do not match.")
        sys.exit(1)
    hashed_password = pwd.get_password_hash(password)

    user_uid = uuid.uuid4()

    user = SuperuserCreate(
        uid=user_uid,
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        password=hashed_password,
        is_active=True,
        is_staff=True,
        is_superuser=True,
        created_by=user_uid,
        modified_by=user_uid,
    )
    asyncio.get_event_loop().run_until_complete(main(user, conn_str))

import os

import asyncpg
from argon2 import PasswordHasher, exceptions
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in .env")

USER_ID = 1

PASSWORD_HASHER = PasswordHasher(
    time_cost=2, memory_cost=19 * 1024, parallelism=1
)


def hash_password(plain_password: str) -> str:
    """
    Принимает обычный пароль и возвращает строку-хеш Argon2id.

    Эту строку и нужно сохранять в БД.
    """
    return PASSWORD_HASHER.hash(plain_password)


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Возвращает True, если введённый пароль соответствует сохранённому хешу,
    иначе False.
    """
    try:
        return PASSWORD_HASHER.verify(stored_hash, plain_password)
    except exceptions.VerifyMismatchError:
        # Пароль не подходит
        return False
    except exceptions.VerificationError:
        # Некорректный формат хеша или другая ошибка верификации
        return False


class ChangePasswordRequest(BaseModel):
    password: str


class CheckPasswordRequest(BaseModel):
    password: str


class CheckPasswordResponse(BaseModel):
    valid: bool


async def get_connection():
    return await asyncpg.connect(DATABASE_URL)


@app.post("/password", status_code=204)
async def change_password(payload: ChangePasswordRequest) -> None:
    """
    Change password for the user with id=1.
    """
    conn = await get_connection()

    try:
        result = await conn.execute(
            "UPDATE users SET password = $1 WHERE id = $2",
            hash_password(payload.password),
            USER_ID,
        )

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="User not found")

    finally:
        await conn.close()


@app.post("/password/check", response_model=CheckPasswordResponse)
async def check_password(
    payload: CheckPasswordRequest,
) -> CheckPasswordResponse:
    """
    Check given password for the user with id=1.
    """
    if "'" in str(USER_ID):
        raise HTTPException(
            status_code=500,
            detail="Incorrect user_id.",
        )
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT password FROM users WHERE id = $1", USER_ID
        )
    finally:
        await conn.close()

    if row is None:
        return CheckPasswordResponse(valid=False)

    stored_password_hash = row["password"]
    return CheckPasswordResponse(
        valid=(verify_password(payload.password, stored_password_hash))
    )

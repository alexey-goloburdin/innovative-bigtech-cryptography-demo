import os

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in .env")

USER_ID = 1


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
            f"UPDATE users SET password = '{payload.password}' "
            f"WHERE id = {USER_ID}"
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
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            f"SELECT password FROM users WHERE id = {USER_ID}"
        )
    finally:
        await conn.close()

    if row is None:
        return CheckPasswordResponse(valid=False)

    stored_password = row["password"]
    return CheckPasswordResponse(valid=(stored_password == payload.password))

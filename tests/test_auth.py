from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from App.routers.auth import (
    ALGORITHM,
    SECRET_KEY,
    authentication_user,
    create_access_token,
    get_current_user,
)


def test_authenticate_user(test_user, db_session):
    authenticated = authentication_user(test_user.username, "test1234", db_session)
    assert authenticated is not None
    assert authenticated.username == test_user.username

    assert authentication_user("WrongUserName", "test1234", db_session) is False
    assert authentication_user(test_user.username, "wrongpass", db_session) is False


def test_create_access_token():
    token = create_access_token("testuser", 1, "user", timedelta(days=1))
    decoded = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False}
    )
    assert decoded["sub"] == "testuser"
    assert decoded["id"] == 1
    assert decoded["role"] == "user"


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token=token)
    assert user == {"username": "testuser", "id": 1, "user_role": "admin"}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "user"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could Not Validate User."

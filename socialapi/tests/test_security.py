import pytest
from .. import security
from ..config import config
from jose import jwt


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 5


def test_create_access_token():
    token = security.create_access_token("test@test.com")
    assert {"sub": "test@test.com"}.items() <= jwt.decode(
        token, key=config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
    ).items()


def test_password_hashes():
    password = "password"
    assert security.verify_password(password, security.get_password_hash(password))


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@test.com")
    assert user is None


@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    user = await security.authenticate_user(
        registered_user["email"], registered_user["password"]
    )
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException) as exc_info:
        await security.authenticate_user("test@test.com", "1234")
    
    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException) as exc_info:
        await security.authenticate_user(registered_user["email"], "random_string")
    
    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"

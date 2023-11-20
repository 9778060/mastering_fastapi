import pytest
from .. import security
from ..config import config
from jose import jwt


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 5


def test_confirmation_token_expire_minutes():
    assert security.confirm_token_expire_minutes() == 5


def test_create_access_token():
    token = security.create_access_token("test@test.com")
    assert {"sub": "test@test.com", "type": "access"}.items() <= jwt.decode(
        token, key=config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
    ).items()


def test_create_confirm_token():
    token = security.create_confirmation_token("test@test.com")
    assert {"sub": "test@test.com", "type": "confirmation"}.items() <= jwt.decode(
        token, key=config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
    ).items()


def test_get_subject_for_token_type_valid_confirmation():
    email = "test@test.com"
    token = security.create_confirmation_token(email)
    assert email == security.get_subject_for_token_type(token, "confirmation")


def test_get_subject_for_token_type_valid_access():
    email = "test@test.com"
    token = security.create_access_token(email)
    assert email == security.get_subject_for_token_type(token, "access")


def test_get_subject_for_token_type_expired(mocker):
    mocker.patch("socialapi.security.access_token_expire_minutes", return_value=-1)
    email = "test@test.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Token has expired"


def test_get_subject_for_token_type_invalid_token():
    token = "invalid token"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"


def test_get_subject_for_token_type_missing_sub():
    email = "test@test.com"
    token = security.create_access_token(email)
    payload = jwt.decode(token, key=config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    del payload["sub"]
    token = jwt.encode(payload, key=config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Token is missing 'sub' field"


def test_get_subject_for_token_type_wrong_type():
    email = "test@test.com"
    token = security.create_confirmation_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Incorrect type, expected access"


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
async def test_authenticate_user(confirmed_user: dict):
    user = await security.authenticate_user(
        confirmed_user["email"], confirmed_user["password"]
    )
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException) as exc_info:
        await security.authenticate_user("test@test.com", "1234")
    
    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Incorrect email or password"


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException) as exc_info:
        await security.authenticate_user(registered_user["email"], "random_string")
    
    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Incorrect email or password"


@pytest.mark.anyio
async def test_get_current_user(confirmed_user: dict):
    token = security.create_access_token(confirmed_user["email"])
    user = await security.get_current_user(token)
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException) as exc_info:
        await security.get_current_user("random_string")

    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"


@pytest.mark.anyio
async def test_get_current_user_wrong_token_type(registered_user: dict):
    token = security.create_confirmation_token(registered_user["email"])
    with pytest.raises(security.HTTPException) as exc_info:
        await security.get_current_user(token)

    assert exc_info.value.status_code == security.status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Incorrect type, expected access"

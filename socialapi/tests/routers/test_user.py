import pytest
from httpx import AsyncClient
import sys
from fastapi import status, Request

from ...main import prefix_users


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(prefix_users + "/register", json={"email": email, "password": password})

@pytest.mark.anyio
async def test_register_users(async_client: AsyncClient):
    email = "test1@test.com"
    password = "1234"

    response = await register_user(async_client, email, password)

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"detail": "User is created", "id": 1}.items() <= response.json().items()

    email = "test2@test.com"
        
    response = await register_user(async_client, email, password)

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"detail": "User is created", "id": 2}.items() <= response.json().items()

    email = "test3@test.com"

    response = await register_user(async_client, email, password)

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"detail": "User is created", "id": 3}.items() <= response.json().items()


@pytest.mark.anyio
async def test_register_user_already_exists(async_client: AsyncClient, registered_user: dict):

    response = await register_user(async_client, registered_user["email"], registered_user["password"])

    print()
    print(response.json())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User already exists" in response.json()["detail"]


@pytest.mark.anyio
async def test_confirm_user(async_client: AsyncClient, mocker):
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, "test@test.com", "1234")

    confirmation_url = str(spy.spy_return)

    response = await async_client.get(confirmation_url)

    assert response.status_code == status.HTTP_200_OK
    assert "User is confirmed" in response.json()["detail"]


@pytest.mark.anyio
async def test_confirm_user_twice(async_client: AsyncClient, mocker):
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, "test@test.com", "1234")

    confirmation_url = str(spy.spy_return)

    response = await async_client.get(confirmation_url)

    assert response.status_code == status.HTTP_200_OK
    assert "User is confirmed" in response.json()["detail"]

    response = await async_client.get(confirmation_url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User already confirmed" in response.json()["detail"]


@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get(prefix_users + "/confirm/invalid_token")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client: AsyncClient, mocker):
    mocker.patch("socialapi.security.confirm_token_expire_minutes", return_value=-1)
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, "test@test.com", "1234")

    confirmation_url = str(spy.spy_return)

    response = await async_client.get(confirmation_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        prefix_users + "/login",
        json={"email": "test@test.com", "password": "1234"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, confirmed_user: dict):
    response = await async_client.post(
        prefix_users + "/login",
        json={
            "email": confirmed_user["email"],
            "password": confirmed_user["password"],
        },
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_login_user_not_confirmed(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        prefix_users + "/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_login_user_incorrect_password(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        prefix_users + "/login",
        json={
            "email": registered_user["email"],
            "password": "random_string",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

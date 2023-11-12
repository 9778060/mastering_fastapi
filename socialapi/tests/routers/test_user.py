import pytest
from httpx import AsyncClient
import sys
from fastapi import status

from ...main import prefix_users


async def register_user(async_client: AsyncClient, email: str, password: str):
    response = await async_client.post(prefix_users + "/register", json={"email": email, "password": password})
    return response.json()

@pytest.mark.anyio
async def test_register_users(async_client: AsyncClient):
    email = "test1@test.com"
    password = "1234"

    response = await async_client.post(
        prefix_users + "/register",
        json={"email": email, "password": password}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"message": "User is created", "id": 1}.items() <= response.json().items()

    email = "test2@test.com"
        
    response = await async_client.post(
        prefix_users + "/register",
        json={"email": email, "password": password}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"message": "User is created", "id": 2}.items() <= response.json().items()

    email = "test3@test.com"

    response = await async_client.post(
        prefix_users + "/register",
        json={"email": email, "password": password}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"message": "User is created", "id": 3}.items() <= response.json().items()

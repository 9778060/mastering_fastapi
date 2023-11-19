import os
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from ..database import database, users_table
from ..main import app, prefix_users

@pytest.fixture
def number_of_posts_to_test():
    return 5

@pytest.fixture
def number_of_comments_to_test():
    return 5

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
def client() -> Generator:
    yield TestClient(app)

@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    query = """ALTER SEQUENCE posts_id_seq RESTART WITH 1"""
    await database.execute(query=query)
    query = """ALTER SEQUENCE comments_id_seq RESTART WITH 1"""
    await database.execute(query=query)
    query = """ALTER SEQUENCE users_id_seq RESTART WITH 1"""
    await database.execute(query=query)
    query = """ALTER SEQUENCE likes_id_seq RESTART WITH 1"""
    await database.execute(query=query)
    yield

    await database.disconnect()

@pytest.fixture
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac


@pytest.fixture
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@test.com", "password": "1234"}
    await async_client.post(prefix_users + "/register", json=user_details)

    print()
    print(user_details)

    query = users_table.select().where(users_table.c.email == user_details["email"])
    user = await database.fetch_one(query)

    user_details["id"] = user.id

    return user_details


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, registered_user: dict) -> str:
    response = await async_client.post(prefix_users + "/login", json=registered_user)
    return response.json()["access_token"]

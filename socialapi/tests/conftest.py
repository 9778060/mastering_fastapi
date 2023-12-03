import os
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, Request, Response
from unittest.mock import AsyncMock, Mock

from ..database import database, users_table, engine, metadata
from ..main import app, prefix_users
from .helpers import create_post

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
    metadata.create_all(engine)

    await database.connect()
    query = """ALTER SEQUENCE posts_id_seq RESTART WITH 1"""
    await database.execute(query=query)
    query = """ALTER SEQUENCE comments_id_seq RESTART WITH 1"""
    await database.execute(query=query)
    query = """ALTER SEQUENCE users_id_seq RESTART WITH 1"""
    await database.execute(query=query)
    query = """ALTER SEQUENCE likes_id_seq RESTART WITH 1"""
    await database.execute(query=query)
    
    yield database

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


@pytest.fixture
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        users_table.update()
        .where(users_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user


@pytest.fixture
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    response = await async_client.post(prefix_users + "/login", json=confirmed_user)
    return response.json()["access_token"]


@pytest.fixture(autouse=True)
def mock_httpx_client(mocker):
    """
    Fixture to mock the HTTPX client so that we never make any
    real HTTP requests (especially important when registering users).
    """
    mocked_client = mocker.patch("socialapi.tasks.httpx.AsyncClient")

    mocked_async_client = Mock()
    response = Response(status_code=200, content="", request=Request("POST", "//"))
    mocked_async_client.post = AsyncMock(return_value=response)
    mocked_client.return_value.__aenter__.return_value = mocked_async_client

    return mocked_async_client


@pytest.fixture
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return [await create_post("Auto created post from pytest", async_client, logged_in_token)]

import os
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from ..database import database
from ..main import app

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

    yield

    await database.disconnect()

@pytest.fixture
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac

from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from ..main import app
from ..routers.post import comments_table, posts_table

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
def client() -> Generator:
    yield TestClient(app)

@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    posts_table.clear()
    comments_table.clear()
    yield

@pytest.fixture
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac

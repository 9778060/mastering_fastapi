import pytest
from httpx import AsyncClient
import sys

from ...main import prefix_posts

async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post(prefix_posts + "/create_post", json={"body": body})
    return response.json()

async def create_comment(body: str, post_id: int, async_client: AsyncClient) -> dict:
    response = await async_client.post(prefix_posts + "/create_comment", json={"body": body, "post_id": post_id})
    return response.json()

@pytest.fixture
async def created_post(async_client: AsyncClient):
    return [await create_post("Auto created post from pytest", async_client)]

@pytest.fixture
async def created_comment(async_client: AsyncClient, created_post: list[dict]):
    return [await create_comment("Auto created comment from pytest", created_post[0]["id"], async_client)]

@pytest.fixture
async def created_posts(async_client: AsyncClient, number_of_posts_to_test: int):
    return [await create_post("Auto created post from pytest", async_client) for i in range(number_of_posts_to_test)]

@pytest.fixture
async def created_comments(async_client: AsyncClient, created_post: list[dict], number_of_comments_to_test: int):
    return [await create_comment("Auto created comment from pytest", created_post[0]["id"], async_client) for i in range(number_of_comments_to_test)]

@pytest.mark.anyio
async def test_create_posts(async_client: AsyncClient):
    body = "Test Post"

    response = await async_client.post(
        prefix_posts + "/create_post", 
        json={"body": body}
    )

    print()
    print(response.json())

    assert response.status_code == 201
    assert {"id": 0, "body": body}.items() <= response.json().items()


    response = await async_client.post(
        prefix_posts + "/create_post", 
        json={"body": body}
    )

    print()
    print(response.json())

    assert response.status_code == 201
    assert {"id": 1, "body": body}.items() <= response.json().items()


    response = await async_client.post(
        prefix_posts + "/create_post", 
        json={"body": body}
    )

    print()
    print(response.json())

    assert response.status_code == 201
    assert {"id": 2, "body": body}.items() <= response.json().items()    


@pytest.mark.anyio
async def test_create_post_without_body(async_client: AsyncClient):
    response = await async_client.post(
        prefix_posts + "/create_post",
        json={}
    )

    print()
    print(response)

    assert response.status_code == 422

@pytest.mark.anyio
async def test_get_all_posts_1_post(async_client: AsyncClient, created_post: list[dict]):

    response = await async_client.get(
        prefix_posts + "/"
    )

    print()
    print(response.json())

    assert response.status_code == 200
    assert response.json() == created_post

@pytest.mark.anyio
async def test_get_all_posts_all_posts(async_client: AsyncClient, created_posts: list[dict]):

    response = await async_client.get(
        prefix_posts + "/"
    )

    print()
    print(response.json())

    assert response.status_code == 200
    assert response.json() == created_posts


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: list[dict]):
    body = "Test Comment"

    response = await async_client.post(
        prefix_posts + "/create_comment", 
        json={"body": body, "post_id": created_post[0]["id"]}
    )

    print()
    print(response.json())

    assert response.status_code == 201
    assert {"id": 0, "body": body, "post_id": created_post[0]["id"]}.items() <= response.json().items()

    response = await async_client.post(
        prefix_posts + "/create_comment", 
        json={"body": body, "post_id": created_post[0]["id"]}
    )

    print()
    print(response.json())

    assert response.status_code == 201
    assert {"id": 1, "body": body, "post_id": created_post[0]["id"]}.items() <= response.json().items()

    response = await async_client.post(
        prefix_posts + "/create_comment", 
        json={"body": body, "post_id": created_post[0]["id"]}
    )

    print()
    print(response.json())

    assert response.status_code == 201
    assert {"id": 2, "body": body, "post_id": created_post[0]["id"]}.items() <= response.json().items()

@pytest.mark.anyio
async def test_get_1_comment_on_post(async_client: AsyncClient, created_post: list[dict], created_comment: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}/comments"
    )

    print()
    print(response.json())

    assert response.status_code == 200
    assert response.json() == created_comment

@pytest.mark.anyio
async def test_get_1_comment_on_post_empty(async_client: AsyncClient, created_post: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}/comments"
    )

    print()
    print(response)

    assert response.status_code == 404
    

@pytest.mark.anyio
async def test_get_all_comments_on_post(async_client: AsyncClient, created_post: list[dict], created_comments: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}/comments"
    )

    print()
    print(response.json())

    assert response.status_code == 200
    assert response.json() == created_comments

@pytest.mark.anyio
async def test_get_post_with_1_comment(async_client: AsyncClient, created_post: list[dict], created_comment: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}"
    )

    print()
    print(response.json())

    assert response.status_code == 200
    assert response.json() == {"post": created_post[0], "comments": created_comment}

@pytest.mark.anyio
async def test_get_post_with_many_comments(async_client: AsyncClient, created_post: list[dict], created_comments: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}"
    )

    print()
    print(response.json())

    assert response.status_code == 200
    assert response.json() == {"post": created_post[0], "comments": created_comments}

@pytest.mark.anyio
async def test_get_missing_post_with_comment(async_client: AsyncClient, created_post: list[dict], created_comment: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/555"
    )

    print()
    print(response.json())

    assert response.status_code == 404

import pytest
from httpx import AsyncClient
import sys
from fastapi import status
from ... import security

from ...main import prefix_posts

async def create_post(body: str, async_client: AsyncClient, logged_in_token: str, with_likes=0) -> dict:
    response = await async_client.post(prefix_posts + "/create_post", json={"body": body}, headers={"Authorization": f"Bearer {logged_in_token}"})
    for i in range(with_likes):
        response_like = await async_client.post(prefix_posts + "/like", json={"post_id": response.json()["id"]}, headers={"Authorization": f"Bearer {logged_in_token}"})
    return response.json()

async def create_comment(body: str, post_id: int, async_client: AsyncClient, logged_in_token: str) -> dict:
    response = await async_client.post(prefix_posts + "/create_comment", json={"body": body, "post_id": post_id}, headers={"Authorization": f"Bearer {logged_in_token}"})
    return response.json()

async def like_post(post_id: int, async_client: AsyncClient, logged_in_token: str) -> dict:
    response = await async_client.post(prefix_posts + "/like", json={"post_id": post_id}, headers={"Authorization": f"Bearer {logged_in_token}"})
    return response.json()

@pytest.fixture
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return [await create_post("Auto created post from pytest", async_client, logged_in_token)]

@pytest.fixture
async def created_post_with_like(async_client: AsyncClient, logged_in_token: str):
    return [await create_post("Auto created post from pytest", async_client, logged_in_token, with_likes=1)]

@pytest.fixture
async def created_comment(async_client: AsyncClient, created_post: list[dict], logged_in_token: str):
    return [await create_comment("Auto created comment from pytest", created_post[0]["id"], async_client, logged_in_token)]

@pytest.fixture
async def created_posts(async_client: AsyncClient, number_of_posts_to_test: int, logged_in_token: str):
    return [await create_post("Auto created post from pytest", async_client, logged_in_token) for i in range(number_of_posts_to_test)]

@pytest.fixture
async def created_posts_with_like(async_client: AsyncClient, number_of_posts_to_test: int, logged_in_token: str):
    return [await create_post("Auto created post from pytest", async_client, logged_in_token, with_likes=number_of_posts_to_test - i) for i in range(number_of_posts_to_test)]

@pytest.fixture
async def created_comments(async_client: AsyncClient, created_post: list[dict], number_of_comments_to_test: int, logged_in_token: str):
    return [await create_comment("Auto created comment from pytest", created_post[0]["id"], async_client, logged_in_token) for i in range(number_of_comments_to_test)]

@pytest.mark.anyio
async def test_create_posts(async_client: AsyncClient, confirmed_user: dict, logged_in_token: str):
    body = "Test Post"

    response = await async_client.post(
        prefix_posts + "/create_post", 
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 1, "body": body, "user_id": confirmed_user["id"]}.items() <= response.json().items()


    response = await async_client.post(
        prefix_posts + "/create_post", 
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 2, "body": body, "user_id": confirmed_user["id"]}.items() <= response.json().items()


    response = await async_client.post(
        prefix_posts + "/create_post", 
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 3, "body": body, "user_id": confirmed_user["id"]}.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_without_body(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.post(
        prefix_posts + "/create_post",
        json={},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_post_expired_token(async_client: AsyncClient, confirmed_user: dict, mocker):
    mocker.patch("socialapi.security.access_token_expire_minutes", return_value=-1)
    token = security.create_access_token(confirmed_user["email"])
    response = await async_client.post(
        prefix_posts + "/create_post",
        json={"body": "Test Post"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
async def test_like_post(async_client: AsyncClient, created_post: list[dict], confirmed_user: dict, logged_in_token: str):

    response = await async_client.post(
        prefix_posts + "/like", 
        json={"post_id": created_post[0]["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 1, "post_id": created_post[0]["id"], "user_id": confirmed_user["id"]}.items() <= response.json().items()


    response = await async_client.post(
        prefix_posts + "/like", 
        json={"post_id": created_post[0]["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 2, "post_id": created_post[0]["id"], "user_id": confirmed_user["id"]}.items() <= response.json().items()


    response = await async_client.post(
        prefix_posts + "/like", 
        json={"post_id": created_post[0]["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 3, "post_id": created_post[0]["id"], "user_id": confirmed_user["id"]}.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_all_posts_1_post(async_client: AsyncClient, created_post_with_like: list[dict]):

    response = await async_client.get(
        prefix_posts + "/"
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert created_post_with_like[0].items() <= response.json()[0].items()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "sorting, expected_order",
    [
        ("new", 1),
        ("old", 0),
    ],
)
async def test_get_all_posts_all_posts_with_sorting(async_client: AsyncClient, created_posts: list[dict], sorting: str, expected_order: int, number_of_posts_to_test: int):

    response = await async_client.get(
        prefix_posts + "/",
        params={"sorting": sorting}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert sorted(response.json(), key=lambda d: d["id"], reverse=expected_order)[0]["id"] == number_of_posts_to_test - number_of_posts_to_test * (1 - expected_order) + (1 - expected_order)


@pytest.mark.anyio
async def test_get_all_posts_all_posts_with_sort_likes(async_client: AsyncClient, created_posts_with_like: list[dict], number_of_posts_to_test: int):

    response = await async_client.get(
        prefix_posts + "/",
        params={"sorting": "most_likes"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert sorted(response.json(), key=lambda d: d["likes"], reverse=True)[0]["likes"] == number_of_posts_to_test


@pytest.mark.anyio
async def test_get_all_posts_all_posts_with_sort_likes_manual(async_client: AsyncClient, logged_in_token: str):

    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    await create_post("Test Post 3", async_client, logged_in_token)
    await like_post(2, async_client, logged_in_token)
    await like_post(2, async_client, logged_in_token)
    await like_post(3, async_client, logged_in_token)

    response = await async_client.get(
        prefix_posts + "/",
        params={"sorting": "most_likes"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert [post["id"] for post in response.json()] == [2, 3, 1]


@pytest.mark.anyio
async def test_get_all_post_wrong_sorting(async_client: AsyncClient):
    response = await async_client.get(prefix_posts + "/", params={"sorting": "wrong"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: list[dict], confirmed_user: dict, logged_in_token: str):
    body = "Test Comment"

    response = await async_client.post(
        prefix_posts + "/create_comment", 
        json={"body": body, "post_id": created_post[0]["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 1, "body": body, "post_id": created_post[0]["id"], "user_id": confirmed_user["id"]}.items() <= response.json().items()

    response = await async_client.post(
        prefix_posts + "/create_comment", 
        json={"body": body, "post_id": created_post[0]["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 2, "body": body, "post_id": created_post[0]["id"], "user_id": confirmed_user["id"]}.items() <= response.json().items()

    response = await async_client.post(
        prefix_posts + "/create_comment", 
        json={"body": body, "post_id": created_post[0]["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 3, "body": body, "post_id": created_post[0]["id"], "user_id": confirmed_user["id"]}.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_1_comment_on_post(async_client: AsyncClient, created_post: list[dict], created_comment: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}/comments"
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == created_comment


@pytest.mark.anyio
async def test_get_1_comment_on_post_empty(async_client: AsyncClient, created_post: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}/comments"
    )

    print()
    print(response)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    

@pytest.mark.anyio
async def test_get_all_comments_on_post(async_client: AsyncClient, created_post: list[dict], created_comments: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}/comments"
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == created_comments


@pytest.mark.anyio
async def test_get_post_with_1_comment(async_client: AsyncClient, created_post: list[dict], created_comment: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}"
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"post": {**created_post[0], "likes": 0}, "comments": created_comment}


@pytest.mark.anyio
async def test_get_post_with_many_comments(async_client: AsyncClient, created_post: list[dict], created_comments: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/{created_post[0]['id']}"
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"post": {**created_post[0], "likes": 0}, "comments": created_comments}


@pytest.mark.anyio
async def test_get_missing_post_with_comment(async_client: AsyncClient, created_post: list[dict], created_comment: list[dict]):
    response = await async_client.get(
        f"{prefix_posts}/555"
    )

    print()
    print(response.json())

    assert response.status_code == status.HTTP_404_NOT_FOUND


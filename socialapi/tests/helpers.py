from httpx import AsyncClient
from ..main import prefix_posts

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

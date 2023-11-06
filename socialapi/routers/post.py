from fastapi import APIRouter, HTTPException
from .. import UserPost, UserPostIn, CommentIn, Comment, UserPostWithComments
from ..database import post_table, comments_table, database
import sys

router = APIRouter()

async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)

@router.post("/create_post", response_model=UserPost, status_code=201)
async def add_post(user_post: UserPostIn):
    data = user_post.model_dump()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/", response_model=list[UserPost])
async def get_posts():
    query = post_table.select()
    return await database.fetch_all(query)


@router.post("/create_comment", response_model=Comment, status_code=201)
async def add_comment(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    query = comments_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/{post_id}/comments", response_model=list[Comment])
async def get_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    found_comments = await database.fetch_all(query)

    if not found_comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    
    return found_comments

@router.get("/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {
        "post": post,
        "comments": await get_comments(post_id)
    }

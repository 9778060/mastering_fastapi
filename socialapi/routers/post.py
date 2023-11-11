from fastapi import APIRouter, HTTPException
from .. import UserPost, UserPostIn, CommentIn, Comment, UserPostWithComments
from ..database import post_table, comments_table, database
import sys
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info("Finding post with id %s", post_id)

    query = post_table.select().where(post_table.c.id == post_id)

    logger.debug(query)

    return await database.fetch_one(query)


@router.post("/create_post", response_model=UserPost, status_code=201)
async def add_post(user_post: UserPostIn):
    logger.info("Creating a post")

    data = user_post.model_dump()
    query = post_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/", response_model=list[UserPost])
async def get_posts():
    logger.info("Getting all posts")
    
    query = post_table.select()

    logger.debug("Message", extra={"email": "name@domain.com"})

    return await database.fetch_all(query)


@router.post("/create_comment", response_model=Comment, status_code=201)
async def add_comment(comment: CommentIn):
    logger.info("Creating a comment")

    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    query = comments_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/{post_id}/comments", response_model=list[Comment])
async def get_comments(post_id: int, error_if_no_comments=True):
    logger.info("Getting comments for a post with id %s", post_id)

    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    query = comments_table.select().where(comments_table.c.post_id == post_id)

    logger.debug(query)

    found_comments = await database.fetch_all(query)

    if error_if_no_comments and not found_comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    
    return found_comments

@router.get("/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info("Getting post with comments; post id %s", post_id)

    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {
        "post": post,
        "comments": await get_comments(post_id, error_if_no_comments=False)
    }

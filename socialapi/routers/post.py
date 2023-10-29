from fastapi import APIRouter, HTTPException
from .. import UserPost, UserPostIn, CommentIn, Comment, UserPostWithComments

posts_table = {}
comments_table = {}

router = APIRouter()

def find_post(post_id: int):
    return posts_table.get(post_id)

@router.post("/create_post", response_model=UserPost, status_code=201)
async def add_post(user_post: UserPostIn):
    data = user_post.model_dump()
    last_record_id = len(posts_table)
    new_post = {**data, "id": last_record_id}
    posts_table[last_record_id] = new_post
    return new_post


@router.get("/", response_model=list[UserPost])
async def get_posts():
    return list(posts_table.values())


@router.post("/create_comment", response_model=Comment, status_code=201)
async def add_comment(comment: CommentIn):
    post = find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    last_record_id = len(comments_table)
    new_comment = {**data, "id": last_record_id}
    comments_table[last_record_id] = new_comment
    return new_comment

@router.get("/{post_id}/comments", response_model=list[Comment])
async def get_comments(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    found_comments = [comment for comment in comments_table.values() if comment["post_id"] == post_id]

    if not found_comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    
    return found_comments

@router.get("/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {
        "post": post,
        "comments": await get_comments(post_id)
    }

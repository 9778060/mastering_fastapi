from fastapi import APIRouter
from ..models import UserPost, UserPostIn

posts_table = {}

router = APIRouter()

@router.post("/create_post", response_model=UserPost)
@router.post("/create_post/", response_model=UserPost)
async def add_post(user_post: UserPostIn):
    data = user_post.model_dump()
    last_record_id = len(posts_table)
    new_post = {**data, "id": last_record_id}
    posts_table[last_record_id] = new_post
    return new_post


@router.get("/", response_model=list[UserPost])
async def get_posts():
    return list(posts_table.values())

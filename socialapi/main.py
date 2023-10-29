from fastapi import FastAPI
from . import post_router

prefix_posts = "/posts"
app = FastAPI()
app.include_router(post_router, prefix=prefix_posts)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

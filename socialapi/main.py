from fastapi import FastAPI
from . import post_router
from contextlib import asynccontextmanager
from .database import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

prefix_posts = "/posts"
app.include_router(post_router, prefix=prefix_posts)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

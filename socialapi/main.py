from fastapi import FastAPI
from . import post_router
from contextlib import asynccontextmanager
from .database import database
from .logging_conf import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

prefix_posts = "/posts"
app.include_router(post_router, prefix=prefix_posts)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

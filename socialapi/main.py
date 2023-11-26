from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from . import post_router
from . import user_router
from . import upload_router
from contextlib import asynccontextmanager
from .database import database
from .logging_conf import configure_logging
import logging
from asgi_correlation_id import CorrelationIdMiddleware


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

prefix_posts = "/posts"
app.include_router(post_router, prefix=prefix_posts)

prefix_users = "/users"
app.include_router(user_router, prefix=prefix_users)

prefix_files = "/files"
app.include_router(upload_router, prefix=prefix_files)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error("HTTPException: %s %s", exc.status_code, exc.detail)
    return await http_exception_handler(request, exc)

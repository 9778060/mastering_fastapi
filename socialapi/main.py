from fastapi import FastAPI
from .routers import post_router

app = FastAPI()
app.include_router(post_router, prefix="/posts")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

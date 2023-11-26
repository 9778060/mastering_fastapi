from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks
import logging
from .. import User, UserIn
from ..security import (
    get_user,
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_credentials_exception,
    get_subject_for_token_type,
    create_confirmation_token
)
from .. import tasks

from ..database import users_table, database

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):

    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    logger.info("Creating a user")

    data = user.model_dump()

    hashed_password = get_password_hash(user.password)
    data["password"] = hashed_password

    query = users_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)

    logger.debug("Submitting background task to send email")

    background_tasks.add_task(
        tasks.send_user_registration_email,
        user.email,
        confirmation_url=request.url_for("confirm_email", token=create_confirmation_token(user.email)),
    )

    return {"detail": "User is created. Please confirm your email", "id": last_record_id}


@router.post("/login")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)

    if not user:
        raise create_credentials_exception("User with this token not found")
    
    access_token = create_access_token(user.email)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirmation")

    logger.debug("Fetching user from the database", extra={"email": email})

    query = users_table.select().where(users_table.c.email == email)

    logger.debug(query)

    result = await database.fetch_one(query)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist")

    logger.debug("Fetching user from the database", extra={"email": email})

    query = users_table.select().where(users_table.c.email == email, users_table.c.confirmed == False)

    logger.debug(query)

    result = await database.fetch_one(query)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already confirmed")

    query = users_table.update().where(users_table.c.email == email).values(confirmed=True)

    logger.debug(query)

    await database.execute(query)

    return {"detail": "User is confirmed"}

from fastapi import APIRouter, HTTPException, status
import logging
from .. import User, UserIn
from ..security import get_user, get_password_hash, authenticate_user, create_access_token, credentials_exception
from ..database import users_table, database

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn):

    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    logger.info("Creating a user")

    data = user.model_dump()

    hashed_password = get_password_hash(user.password)
    data["password"] = hashed_password

    query = users_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)

    return {"detail": "User is created", "id": last_record_id}


@router.post("/login")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)

    if not user:
        raise credentials_exception
    
    access_token = create_access_token(user.email)

    return {"access_token": access_token, "token_type": "bearer"}

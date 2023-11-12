from .database import database, users_table
import logging
from jose import ExpiredSignatureError, JWTError, jwt
import bcrypt

logger = logging.getLogger(__name__)

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password, hashed_password)


async def get_user(email: str):
    logger.debug("Fetching user from the database", extra={"email": email})

    query = users_table.select().where(users_table.c.email == email)

    logger.debug(query)

    result = await database.fetch_one(query)

    if result:
        return result

    return None

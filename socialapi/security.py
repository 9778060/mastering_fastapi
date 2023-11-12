from .database import database, users_table
import logging
from jose import ExpiredSignatureError, JWTError, jwt
import bcrypt
import datetime
from .config import config
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def access_token_expire_minutes() -> int:
    return 5


def create_access_token(email: str):
    logger.debug("Creating access token", extra={"email": email})

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, key=config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    return encoded_jwt


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


async def get_user(email: str):
    logger.debug("Fetching user from the database", extra={"email": email})

    query = users_table.select().where(users_table.c.email == email)

    logger.debug(query)

    result = await database.fetch_one(query)

    if not result:
        return None

    return result


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)

    if not user:
        raise credentials_exception
    
    if not verify_password(password, user.password):
        raise credentials_exception
    
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, key=config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        email = payload.get("sub")

        print("TEST")
        print(email)

        if not email:
            raise credentials_exception
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise credentials_exception from e
    
    user = await get_user(email)

    if not user:
        raise credentials_exception

    return user

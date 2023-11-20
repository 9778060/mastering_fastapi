from .database import database, users_table
import logging
from jose import ExpiredSignatureError, JWTError, jwt
import bcrypt
import datetime
from .config import config
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Literal


logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def access_token_expire_minutes() -> int:
    return 5


def confirm_token_expire_minutes() -> int:
    return 5


def create_access_token(email: str):
    logger.debug("Creating access token", extra={"email": email})

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(jwt_data, key=config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    return encoded_jwt


def create_confirmation_token(email: str):
    logger.debug("Creating confirmation token", extra={"email": email})

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=confirm_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "confirmation"}
    encoded_jwt = jwt.encode(jwt_data, key=config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    return encoded_jwt


def get_subject_for_token_type(token: str, type: Literal["access", "confirmation"]) -> str:
    try:
        payload = jwt.decode(token, key=config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except ExpiredSignatureError as e:
        raise create_credentials_exception("Token has expired") from e
    except JWTError as e:
        raise create_credentials_exception("Invalid token") from e

    email = payload.get("sub")

    if not email:
        raise create_credentials_exception("Token is missing 'sub' field")
    
    token_type = payload.get("type")

    if not token_type or token_type != type:
        raise create_credentials_exception("Incorrect type, expected %s" % (type))

    return email

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
        raise create_credentials_exception("Incorrect email or password")
    
    if not verify_password(password, user.password):
        raise create_credentials_exception("Incorrect email or password")
    
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    email = get_subject_for_token_type(token, "access")

    user = await get_user(email)

    if not user:
        raise create_credentials_exception("Incorrect token")

    return user

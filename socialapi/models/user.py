from pydantic import BaseModel


class UserBase(BaseModel):
    email: str

class User(UserBase):
    id: int

class UserIn(UserBase):
    password: str

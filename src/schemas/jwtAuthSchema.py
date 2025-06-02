from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_type: Optional[str] = None


class APIUserSchema(BaseModel):
    username: str
    password: str
    user_type: Optional[str] = 'user'
    is_active: Optional[bool] = True


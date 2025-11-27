
from datetime import datetime

from pydantic import EmailStr

from app.api.v1.schemas.base import BaseSchema


class UserResponse(BaseSchema):

    id: int
    email: EmailStr
    name: str
    created_at: datetime


class UserBriefResponse(BaseSchema):

    id: int
    name: str
    email: EmailStr
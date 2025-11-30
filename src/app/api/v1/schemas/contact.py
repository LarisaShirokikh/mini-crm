from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.api.v1.schemas.base import BaseSchema, PaginatedResponse
from app.api.v1.schemas.user import UserBriefResponse


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)


class ContactResponse(BaseSchema):
    id: int
    organization_id: int
    owner_id: int
    name: str
    email: str | None
    phone: str | None
    created_at: datetime


class ContactDetailResponse(ContactResponse):
    owner: UserBriefResponse | None = None


class ContactListResponse(PaginatedResponse):
    items: list[ContactResponse]
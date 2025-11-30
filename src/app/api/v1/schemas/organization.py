
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.api.v1.schemas.base import BaseSchema
from app.models.enums import OrganizationRole


class OrganizationResponse(BaseSchema):
    id: int
    name: str
    created_at: datetime


class OrganizationWithRoleResponse(BaseSchema):
    id: int
    name: str
    created_at: datetime
    role: OrganizationRole


class MemberResponse(BaseSchema):
    id: int
    user_id: int
    user_name: str
    user_email: str
    role: OrganizationRole


class AddMemberRequest(BaseModel):
    email: EmailStr
    role: OrganizationRole = Field(default=OrganizationRole.MEMBER)


class UpdateMemberRoleRequest(BaseModel):
    role: OrganizationRole
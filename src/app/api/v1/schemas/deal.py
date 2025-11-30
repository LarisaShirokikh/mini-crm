
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.api.v1.schemas.base import BaseSchema, PaginatedResponse
from app.api.v1.schemas.user import UserBriefResponse
from app.models.enums import DealStage, DealStatus


class DealCreate(BaseModel):
    contact_id: int
    title: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class DealUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    status: DealStatus | None = None
    stage: DealStage | None = None
    contact_id: int | None = None


class DealResponse(BaseSchema):
    id: int
    organization_id: int
    contact_id: int
    owner_id: int
    title: str
    amount: Decimal
    currency: str
    status: DealStatus
    stage: DealStage
    created_at: datetime
    updated_at: datetime


class DealDetailResponse(DealResponse):
    owner: UserBriefResponse | None = None


class DealListResponse(PaginatedResponse):
    items: list[DealResponse]
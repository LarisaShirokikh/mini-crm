from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.user import UserBriefResponse
from app.models.enums import ActivityType


class ActivityCreate(BaseModel):
    type: ActivityType = Field(default=ActivityType.COMMENT)
    payload: dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "comment",
                "payload": {"text": "Client requested updated proposal"},
            }
        }


class ActivityResponse(BaseSchema):
    id: int
    deal_id: int
    author_id: int | None
    type: ActivityType
    payload: dict[str, Any]
    created_at: datetime


class ActivityDetailResponse(ActivityResponse):
    author: UserBriefResponse | None = None


class ActivityListResponse(BaseSchema):
    items: list[ActivityDetailResponse]
    total: int
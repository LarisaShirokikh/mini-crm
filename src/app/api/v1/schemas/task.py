from datetime import date, datetime
from pydantic import BaseModel, Field
from app.api.v1.schemas.base import BaseSchema, PaginatedResponse


class TaskCreate(BaseModel):
    deal_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    is_done: bool | None = None


class TaskResponse(BaseSchema):
    id: int
    deal_id: int
    title: str
    description: str | None
    due_date: date | None
    is_done: bool
    created_at: datetime


class TaskListResponse(PaginatedResponse):
    items: list[TaskResponse]
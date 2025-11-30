
from decimal import Decimal

from pydantic import BaseModel

from app.api.v1.schemas.base import BaseSchema


class StatusSummary(BaseModel):
    count: int
    total_amount: Decimal


class NewDealsInfo(BaseModel):
    count: int
    days: int


class DealsSummaryResponse(BaseSchema):
    by_status: dict[str, StatusSummary]
    average_won_amount: Decimal
    new_deals_last_n_days: NewDealsInfo


class StageConversion(BaseModel):
    from_stage: str
    to_stage: str
    from_count: int
    to_count: int
    conversion_rate: float


class FunnelResponse(BaseSchema):
    stages: dict[str, dict[str, int]]
    stage_totals: dict[str, int]
    conversions: list[StageConversion]
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from typing import Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import analytics_cache
from app.models.deal import Deal
from app.models.enums import DealStage, DealStatus
from app.repositories.deal import DealRepository


def get_enum_value(value: Any) -> str:
    """Get string value from enum or return string as-is."""
    return value.value if hasattr(value, 'value') else value


def _serialize_decimals(data: dict) -> dict:
    """Convert Decimal values to float for caching."""
    result = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, dict):
            result[key] = _serialize_decimals(value)
        else:
            result[key] = value
    return result


class AnalyticsService:
    """Service for analytics with in-memory caching."""

    CACHE_TTL = 60  # Cache for 60 seconds

    def __init__(
            self,
            deal_repo: DealRepository,
            session: AsyncSession,
    ) -> None:
        self.deal_repo = deal_repo
        self.session = session

    async def get_deals_summary(
            self,
            organization_id: int,
            days: int = 30,
    ) -> dict:
        """
        Get deals summary for organization (cached).

        Returns:
            - count by status
            - sum by status
            - average won amount
            - new deals in last N days
        """
        # Check cache first
        cache_key = f"summary:{organization_id}:{days}"
        cached = analytics_cache.get(cache_key)
        if cached is not None:
            return cached

        # Get summary by status
        status_summary = await self.deal_repo.get_summary_by_status(organization_id)

        # Build response
        by_status = {
            status.value: {"count": 0, "total_amount": Decimal("0")}
            for status in DealStatus
        }

        for item in status_summary:
            status_value = get_enum_value(item["status"])
            by_status[status_value] = {
                "count": item["count"],
                "total_amount": item["total_amount"],
            }

        # Get average won amount
        avg_won = await self.deal_repo.get_avg_won_amount(organization_id)

        # Get new deals count in last N days
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        query = (
            select(func.count())
            .select_from(Deal)
            .where(
                and_(
                    Deal.organization_id == organization_id,
                    Deal.created_at >= cutoff_date,
                )
            )
        )
        result = await self.session.execute(query)
        new_deals_count = result.scalar() or 0

        response = {
            "by_status": by_status,
            "average_won_amount": avg_won,
            "new_deals_last_n_days": {
                "count": new_deals_count,
                "days": days,
            },
        }

        # Cache the result (serialize decimals for JSON compatibility)
        analytics_cache.set(cache_key, _serialize_decimals(response), self.CACHE_TTL)

        return response

    async def get_deals_funnel(self, organization_id: int) -> dict:
        """
        Get sales funnel data (cached).

        Returns:
            - count by stage and status
            - conversion rates between stages
        """
        # Check cache first
        cache_key = f"funnel:{organization_id}"
        cached = analytics_cache.get(cache_key)
        if cached is not None:
            return cached

        funnel_data = await self.deal_repo.get_funnel_data(organization_id)

        # Build stages breakdown
        stages: dict[str, dict[str, int]] = {}
        stage_totals: dict[str, int] = {}

        for item in funnel_data:
            stage_name = get_enum_value(item["stage"])
            status_name = get_enum_value(item["status"])

            if stage_name not in stages:
                stages[stage_name] = {}
                stage_totals[stage_name] = 0

            stages[stage_name][status_name] = item["count"]
            stage_totals[stage_name] += item["count"]

        # Calculate conversion rates
        stage_order = [stage.value for stage in DealStage]
        conversions = []

        for i in range(len(stage_order) - 1):
            from_stage = stage_order[i]
            to_stage = stage_order[i + 1]

            from_count = stage_totals.get(from_stage, 0)
            to_count = stage_totals.get(to_stage, 0)

            if from_count > 0:
                rate = round((to_count / from_count) * 100, 2)
            else:
                rate = 0.0

            conversions.append({
                "from_stage": from_stage,
                "to_stage": to_stage,
                "from_count": from_count,
                "to_count": to_count,
                "conversion_rate": rate,
            })

        response = {
            "stages": stages,
            "stage_totals": stage_totals,
            "conversions": conversions,
        }

        # Cache the result
        analytics_cache.set(cache_key, response, self.CACHE_TTL)

        return response

    @staticmethod
    def invalidate_cache(organization_id: int) -> None:
        """Invalidate analytics cache for organization."""
        analytics_cache.invalidate_prefix(f"summary:{organization_id}")
        analytics_cache.invalidate_prefix(f"funnel:{organization_id}")
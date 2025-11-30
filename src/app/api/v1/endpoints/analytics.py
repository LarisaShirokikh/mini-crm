"""Analytics endpoints."""

from fastapi import APIRouter, Query

from app.api.v1.dependencies import CurrentMembership, DbSession, OrganizationId
from app.api.v1.schemas import DealsSummaryResponse, FunnelResponse
from app.repositories.deal import DealRepository
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(session: DbSession) -> AnalyticsService:
    return AnalyticsService(
        deal_repo=DealRepository(session),
        session=session,
    )


@router.get("/deals/summary", response_model=DealsSummaryResponse)
async def get_deals_summary(
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
    days: int = Query(default=30, ge=1, le=365),
) -> DealsSummaryResponse:
    """
    Get deals summary for the organization.

    Returns:
    - Count and total amount by status
    - Average amount of won deals
    - Number of new deals in last N days
    """
    analytics_service = get_analytics_service(session)
    summary = await analytics_service.get_deals_summary(
        organization_id=organization_id,
        days=days,
    )

    return DealsSummaryResponse(**summary)


@router.get("/deals/funnel", response_model=FunnelResponse)
async def get_deals_funnel(
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> FunnelResponse:
    """
    Get sales funnel data.

    Returns:
    - Deal count by stage and status
    - Conversion rates between stages
    """
    analytics_service = get_analytics_service(session)
    funnel = await analytics_service.get_deals_funnel(
        organization_id=organization_id,
    )

    return FunnelResponse(**funnel)
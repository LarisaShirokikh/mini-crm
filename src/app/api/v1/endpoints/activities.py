from fastapi import APIRouter, Query

from app.api.v1.dependencies import CurrentMembership, DbSession, OrganizationId
from app.api.v1.schemas import (
    ActivityCreate,
    ActivityDetailResponse,
    ActivityListResponse,
)
from app.api.v1.schemas.user import UserBriefResponse
from app.core.exceptions import ForbiddenException
from app.models.enums import ActivityType
from app.repositories.activity import ActivityRepository
from app.repositories.deal import DealRepository
from app.services.deal import DealService

router = APIRouter(prefix="/deals/{deal_id}/activities", tags=["Activities"])


@router.get("", response_model=ActivityListResponse)
async def list_activities(
    deal_id: int,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> ActivityListResponse:
    # Verify deal belongs to organization
    deal_repo = DealRepository(session)
    deal = await deal_repo.get_by_id(deal_id)

    if not deal or deal.organization_id != organization_id:
        from app.core.exceptions import DealNotFoundException
        raise DealNotFoundException()

    activity_repo = ActivityRepository(session)
    activities = await activity_repo.get_by_deal(
        deal_id=deal_id,
        skip=skip,
        limit=limit,
    )

    items = []
    for activity in activities:
        author = None
        if activity.author:
            author = UserBriefResponse(
                id=activity.author.id,
                name=activity.author.name,
                email=activity.author.email,
            )

        items.append(
            ActivityDetailResponse(
                id=activity.id,
                deal_id=activity.deal_id,
                author_id=activity.author_id,
                type=activity.type,
                payload=activity.payload,
                created_at=activity.created_at,
                author=author,
            )
        )

    return ActivityListResponse(
        items=items,
        total=len(items),
    )


@router.post("", response_model=ActivityDetailResponse, status_code=201)
async def create_activity(
    deal_id: int,
    data: ActivityCreate,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> ActivityDetailResponse:
    # Only comments can be created manually
    if data.type != ActivityType.COMMENT:
        raise ForbiddenException(
            message="Only comments can be created manually"
        )

    # Verify deal belongs to organization
    deal_repo = DealRepository(session)
    deal = await deal_repo.get_by_id(deal_id)

    if not deal or deal.organization_id != organization_id:
        from app.core.exceptions import DealNotFoundException
        raise DealNotFoundException()

    activity_repo = ActivityRepository(session)

    text = data.payload.get("text", "")
    activity = await activity_repo.create_comment(
        deal_id=deal_id,
        author_id=membership.user_id,
        text=text,
    )

    # Refresh to get author relation
    from app.repositories.user import UserRepository
    user_repo = UserRepository(session)
    author = await user_repo.get_by_id(membership.user_id)

    return ActivityDetailResponse(
        id=activity.id,
        deal_id=activity.deal_id,
        author_id=activity.author_id,
        type=activity.type,
        payload=activity.payload,
        created_at=activity.created_at,
        author=UserBriefResponse(
            id=author.id,
            name=author.name,
            email=author.email,
        ) if author else None,
    )
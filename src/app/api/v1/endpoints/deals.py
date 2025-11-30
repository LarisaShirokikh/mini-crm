from decimal import Decimal

from fastapi import APIRouter, Query

from app.api.v1.dependencies import CurrentMembership, DbSession, OrganizationId
from app.api.v1.schemas import (
    DealCreate,
    DealListResponse,
    DealResponse,
    DealUpdate,
)
from app.models.enums import DealStage, DealStatus
from app.repositories.activity import ActivityRepository
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository
from app.services.deal import DealService

router = APIRouter(prefix="/deals", tags=["Deals"])


def get_deal_service(session: DbSession) -> DealService:
    return DealService(
        deal_repo=DealRepository(session),
        contact_repo=ContactRepository(session),
        activity_repo=ActivityRepository(session),
    )


@router.get("", response_model=DealListResponse)
async def list_deals(
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: list[DealStatus] | None = Query(default=None),
    stage: DealStage | None = None,
    owner_id: int | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    order_by: str = Query(default="created_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> DealListResponse:
    deal_service = get_deal_service(session)

    deals, total = await deal_service.get_deals(
        organization_id=organization_id,
        membership=membership,
        page=page,
        page_size=page_size,
        status=status,
        stage=stage,
        owner_id=owner_id,
        min_amount=min_amount,
        max_amount=max_amount,
        order_by=order_by,
        order=order,
    )

    pages = (total + page_size - 1) // page_size

    return DealListResponse(
        items=deals,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("", response_model=DealResponse, status_code=201)
async def create_deal(
    data: DealCreate,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> DealResponse:
    deal_service = get_deal_service(session)

    deal = await deal_service.create_deal(
        organization_id=organization_id,
        owner_id=membership.user_id,
        contact_id=data.contact_id,
        title=data.title,
        amount=data.amount,
        currency=data.currency,
    )

    return DealResponse.model_validate(deal)


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> DealResponse:
    deal_service = get_deal_service(session)
    deal = await deal_service.get_deal(deal_id, organization_id)
    return DealResponse.model_validate(deal)


@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    data: DealUpdate,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> DealResponse:
    deal_service = get_deal_service(session)

    update_data = data.model_dump(exclude_unset=True)
    deal = await deal_service.update_deal(
        deal_id=deal_id,
        organization_id=organization_id,
        membership=membership,
        **update_data,
    )

    return DealResponse.model_validate(deal)


@router.delete("/{deal_id}", status_code=204)
async def delete_deal(
    deal_id: int,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> None:
    deal_service = get_deal_service(session)

    await deal_service.delete_deal(
        deal_id=deal_id,
        organization_id=organization_id,
        membership=membership,
    )
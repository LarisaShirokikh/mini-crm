from decimal import Decimal

from app.core.exceptions import (
    ContactNotFoundException,
    CrossOrganizationException,
    DealNotFoundException,
    ForbiddenException,
    InvalidDealAmountException,
    InvalidStageTransitionException,
)
from app.models.deal import Deal
from app.models.enums import DealStage, DealStatus
from app.models.organization_member import OrganizationMember
from app.repositories.activity import ActivityRepository
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository


def get_enum_value(value) -> str:
    """Get string value from enum or return string as-is."""
    return value.value if hasattr(value, 'value') else value


class DealService:

    def __init__(
        self,
        deal_repo: DealRepository,
        contact_repo: ContactRepository,
        activity_repo: ActivityRepository,
    ) -> None:
        self.deal_repo = deal_repo
        self.contact_repo = contact_repo
        self.activity_repo = activity_repo

    async def get_deals(
        self,
        organization_id: int,
        membership: OrganizationMember,
        *,
        page: int = 1,
        page_size: int = 20,
        status: list[DealStatus] | None = None,
        stage: DealStage | None = None,
        owner_id: int | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[Deal], int]:

        # Members can only see their own deals' owner filter
        if not membership.can_manage_all_entities() and owner_id:
            if owner_id != membership.user_id:
                owner_id = membership.user_id

        skip = (page - 1) * page_size

        deals = await self.deal_repo.get_by_organization(
            organization_id,
            skip=skip,
            limit=page_size,
            status=status,
            stage=stage,
            owner_id=owner_id,
            min_amount=min_amount,
            max_amount=max_amount,
            order_by=order_by,
            order=order,
        )

        total = await self.deal_repo.count_by_organization(organization_id, status)

        return deals, total

    async def get_deal(
        self,
        deal_id: int,
        organization_id: int,
    ) -> Deal:

        deal = await self.deal_repo.get_by_id(deal_id)

        if not deal or deal.organization_id != organization_id:
            raise DealNotFoundException()

        return deal

    async def create_deal(
        self,
        organization_id: int,
        owner_id: int,
        contact_id: int,
        title: str,
        amount: Decimal = Decimal("0"),
        currency: str = "USD",
    ) -> Deal:

        # Verify contact belongs to same organization
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact or contact.organization_id != organization_id:
            raise ContactNotFoundException()

        return await self.deal_repo.create(
            organization_id=organization_id,
            owner_id=owner_id,
            contact_id=contact_id,
            title=title,
            amount=amount,
            currency=currency,
            status=DealStatus.NEW,
            stage=DealStage.QUALIFICATION,
        )

    async def update_deal(
        self,
        deal_id: int,
        organization_id: int,
        membership: OrganizationMember,
        **kwargs,
    ) -> Deal:

        deal = await self.get_deal(deal_id, organization_id)

        # Check permissions
        if not membership.can_manage_all_entities():
            if deal.owner_id != membership.user_id:
                raise ForbiddenException()

        # Validate status change
        new_status = kwargs.get("status")
        if new_status and new_status != deal.status:
            await self._validate_status_change(deal, new_status, kwargs.get("amount"))
            # Create activity
            await self.activity_repo.create_status_changed(
                deal_id=deal.id,
                author_id=membership.user_id,
                old_status=get_enum_value(deal.status),
                new_status=get_enum_value(new_status),
            )

        # Validate stage change
        new_stage = kwargs.get("stage")
        if new_stage and new_stage != deal.stage:
            self._validate_stage_change(deal.stage, new_stage, membership)
            # Create activity
            await self.activity_repo.create_stage_changed(
                deal_id=deal.id,
                author_id=membership.user_id,
                old_stage=get_enum_value(deal.stage),
                new_stage=get_enum_value(new_stage),
            )

        # Validate contact if changing
        new_contact_id = kwargs.get("contact_id")
        if new_contact_id and new_contact_id != deal.contact_id:
            contact = await self.contact_repo.get_by_id(new_contact_id)
            if not contact or contact.organization_id != organization_id:
                raise CrossOrganizationException()

        return await self.deal_repo.update(deal, **kwargs)

    async def delete_deal(
        self,
        deal_id: int,
        organization_id: int,
        membership: OrganizationMember,
    ) -> None:

        deal = await self.get_deal(deal_id, organization_id)

        if not membership.can_manage_all_entities():
            if deal.owner_id != membership.user_id:
                raise ForbiddenException()

        await self.deal_repo.delete(deal)

    async def _validate_status_change(
        self,
        deal: Deal,
        new_status: DealStatus,
        new_amount: Decimal | None,
    ) -> None:

        amount = new_amount if new_amount is not None else deal.amount

        # Cannot close as won with amount <= 0
        if new_status == DealStatus.WON and amount <= 0:
            raise InvalidDealAmountException()

    def _validate_stage_change(
        self,
        current_stage: DealStage,
        new_stage: DealStage,
        membership: OrganizationMember,
    ) -> None:

        if DealStage.is_backward_transition(current_stage, new_stage):
            if not membership.can_rollback_stage():
                raise InvalidStageTransitionException()
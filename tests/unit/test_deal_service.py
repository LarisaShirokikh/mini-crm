import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import (
    InvalidDealAmountException,
    InvalidStageTransitionException,
)
from app.models.deal import Deal
from app.models.enums import DealStage, DealStatus, OrganizationRole
from app.models.organization_member import OrganizationMember
from app.services.deal import DealService


class TestDealStatusValidation:
    """Tests for deal status change validation."""

    def __init__(self):
        pass

    @pytest.fixture
    def deal_service(self):
        """Create deal service with mocked repos."""
        return DealService(
            deal_repo=AsyncMock(),
            contact_repo=AsyncMock(),
            activity_repo=AsyncMock(),
        )

    @pytest.fixture
    def existing_deal(self):
        """Create a mock existing deal."""
        deal = MagicMock(spec=Deal)
        deal.id = 1
        deal.amount = Decimal("1000.00")
        deal.status = DealStatus.IN_PROGRESS
        deal.stage = DealStage.PROPOSAL
        return deal

    @pytest.mark.asyncio
    async def test_cannot_win_deal_with_zero_amount(self, deal_service, existing_deal):
        """Cannot close deal as won with zero amount."""
        existing_deal.amount = Decimal("0")
        
        with pytest.raises(InvalidDealAmountException):
            await deal_service._validate_status_change(
                deal=existing_deal,
                new_status=DealStatus.WON,
                new_amount=None,
            )

    @pytest.mark.asyncio
    async def test_cannot_win_deal_with_negative_amount(self, deal_service, existing_deal):
        """Cannot close deal as won with negative amount."""
        existing_deal.amount = Decimal("-100")
        
        with pytest.raises(InvalidDealAmountException):
            await deal_service._validate_status_change(
                deal=existing_deal,
                new_status=DealStatus.WON,
                new_amount=None,
            )

    @pytest.mark.asyncio
    async def test_can_win_deal_with_positive_amount(self, deal_service, existing_deal):
        """Can close deal as won with positive amount."""
        existing_deal.amount = Decimal("1000.00")
        
        # Should not raise
        await deal_service._validate_status_change(
            deal=existing_deal,
            new_status=DealStatus.WON,
            new_amount=None,
        )

    @pytest.mark.asyncio
    async def test_can_win_deal_with_new_positive_amount(self, deal_service, existing_deal):
        """Can close deal as won if new amount is positive."""
        existing_deal.amount = Decimal("0")
        
        # Should not raise because new_amount is positive
        await deal_service._validate_status_change(
            deal=existing_deal,
            new_status=DealStatus.WON,
            new_amount=Decimal("500.00"),
        )

    @pytest.mark.asyncio
    async def test_can_lose_deal_with_zero_amount(self, deal_service, existing_deal):
        """Can close deal as lost with zero amount."""
        existing_deal.amount = Decimal("0")
        
        # Should not raise
        await deal_service._validate_status_change(
            deal=existing_deal,
            new_status=DealStatus.LOST,
            new_amount=None,
        )


class TestDealStageValidation:
    """Tests for deal stage transition validation."""

    def __init__(self):
        pass

    @pytest.fixture
    def deal_service(self):
        """Create deal service with mocked repos."""
        return DealService(
            deal_repo=AsyncMock(),
            contact_repo=AsyncMock(),
            activity_repo=AsyncMock(),
        )

    @pytest.fixture
    def owner_membership(self):
        """Create owner membership."""
        member = MagicMock(spec=OrganizationMember)
        member.role = OrganizationRole.OWNER
        member.can_rollback_stage.return_value = True
        return member

    @pytest.fixture
    def member_membership(self):
        """Create regular member membership."""
        member = MagicMock(spec=OrganizationMember)
        member.role = OrganizationRole.MEMBER
        member.can_rollback_stage.return_value = False
        return member

    def test_forward_transition_allowed_for_member(self, deal_service, member_membership):
        """Forward stage transition is allowed for member."""
        # Should not raise
        deal_service._validate_stage_change(
            current_stage=DealStage.QUALIFICATION,
            new_stage=DealStage.PROPOSAL,
            membership=member_membership,
        )

    def test_backward_transition_blocked_for_member(self, deal_service, member_membership):
        """Backward stage transition is blocked for member."""
        with pytest.raises(InvalidStageTransitionException):
            deal_service._validate_stage_change(
                current_stage=DealStage.PROPOSAL,
                new_stage=DealStage.QUALIFICATION,
                membership=member_membership,
            )

    def test_backward_transition_allowed_for_owner(self, deal_service, owner_membership):
        """Backward stage transition is allowed for owner."""
        # Should not raise
        deal_service._validate_stage_change(
            current_stage=DealStage.PROPOSAL,
            new_stage=DealStage.QUALIFICATION,
            membership=owner_membership,
        )
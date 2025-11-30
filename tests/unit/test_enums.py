"""Tests for enums."""

import pytest

from app.models.enums import DealStage, DealStatus, OrganizationRole


class TestOrganizationRole:
    """Tests for OrganizationRole enum."""

    def test_can_manage_organization_owner(self):
        """Owner can manage organization."""
        assert OrganizationRole.can_manage_organization(OrganizationRole.OWNER) is True

    def test_can_manage_organization_admin(self):
        """Admin can manage organization."""
        assert OrganizationRole.can_manage_organization(OrganizationRole.ADMIN) is True

    def test_can_manage_organization_manager(self):
        """Manager cannot manage organization."""
        assert OrganizationRole.can_manage_organization(OrganizationRole.MANAGER) is False

    def test_can_manage_organization_member(self):
        """Member cannot manage organization."""
        assert OrganizationRole.can_manage_organization(OrganizationRole.MEMBER) is False

    def test_can_manage_all_entities(self):
        """Owner, admin, manager can manage all entities."""
        assert OrganizationRole.can_manage_all_entities(OrganizationRole.OWNER) is True
        assert OrganizationRole.can_manage_all_entities(OrganizationRole.ADMIN) is True
        assert OrganizationRole.can_manage_all_entities(OrganizationRole.MANAGER) is True
        assert OrganizationRole.can_manage_all_entities(OrganizationRole.MEMBER) is False

    def test_can_rollback_stage(self):
        """Only owner and admin can rollback stage."""
        assert OrganizationRole.can_rollback_stage(OrganizationRole.OWNER) is True
        assert OrganizationRole.can_rollback_stage(OrganizationRole.ADMIN) is True
        assert OrganizationRole.can_rollback_stage(OrganizationRole.MANAGER) is False
        assert OrganizationRole.can_rollback_stage(OrganizationRole.MEMBER) is False


class TestDealStatus:
    """Tests for DealStatus enum."""

    def test_is_closed_won(self):
        """Won status is closed."""
        assert DealStatus.WON.is_closed() is True

    def test_is_closed_lost(self):
        """Lost status is closed."""
        assert DealStatus.LOST.is_closed() is True

    def test_is_closed_new(self):
        """New status is not closed."""
        assert DealStatus.NEW.is_closed() is False

    def test_is_closed_in_progress(self):
        """In progress status is not closed."""
        assert DealStatus.IN_PROGRESS.is_closed() is False


class TestDealStage:
    """Tests for DealStage enum."""

    def test_stage_order(self):
        """Stages have correct order."""
        assert DealStage.get_order(DealStage.QUALIFICATION) == 1
        assert DealStage.get_order(DealStage.PROPOSAL) == 2
        assert DealStage.get_order(DealStage.NEGOTIATION) == 3
        assert DealStage.get_order(DealStage.CLOSED) == 4

    def test_is_forward_transition(self):
        """Forward transitions are detected correctly."""
        assert DealStage.is_forward_transition(
            DealStage.QUALIFICATION, DealStage.PROPOSAL
        ) is True
        assert DealStage.is_forward_transition(
            DealStage.PROPOSAL, DealStage.QUALIFICATION
        ) is False

    def test_is_backward_transition(self):
        """Backward transitions are detected correctly."""
        assert DealStage.is_backward_transition(
            DealStage.PROPOSAL, DealStage.QUALIFICATION
        ) is True
        assert DealStage.is_backward_transition(
            DealStage.QUALIFICATION, DealStage.PROPOSAL
        ) is False
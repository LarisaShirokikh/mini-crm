"""Integration tests for deals endpoints."""

import pytest
from decimal import Decimal
from httpx import AsyncClient

from app.models import Deal
from app.models.enums import DealStage, DealStatus


class TestListDeals:
    """Tests for list deals endpoint."""

    @pytest.mark.asyncio
    async def test_list_deals_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can list deals."""
        response = await client.get(
            "/api/v1/deals",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_deals_filter_by_status(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can filter deals by status."""
        response = await client.get(
            "/api/v1/deals",
            headers=auth_headers_with_org,
            params={"status": "new"},
        )

        assert response.status_code == 200
        data = response.json()

        for item in data["items"]:
            assert item["status"] == "new"

    @pytest.mark.asyncio
    async def test_list_deals_filter_by_stage(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can filter deals by stage."""
        response = await client.get(
            "/api/v1/deals",
            headers=auth_headers_with_org,
            params={"stage": "qualification"},
        )

        assert response.status_code == 200
        data = response.json()

        for item in data["items"]:
            assert item["stage"] == "qualification"


class TestCreateDeal:
    """Tests for create deal endpoint."""

    @pytest.mark.asyncio
    async def test_create_deal_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_contact,
    ):
        """Can create a deal."""
        response = await client.post(
            "/api/v1/deals",
            headers=auth_headers_with_org,
            json={
                "contact_id": test_contact.id,
                "title": "New Deal",
                "amount": "5000.00",
                "currency": "USD",
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == "New Deal"
        assert Decimal(data["amount"]) == Decimal("5000.00")
        assert data["currency"] == "USD"
        assert data["status"] == "new"
        assert data["stage"] == "qualification"

    @pytest.mark.asyncio
    async def test_create_deal_invalid_contact(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_member,
    ):
        """Cannot create deal with nonexistent contact."""
        response = await client.post(
            "/api/v1/deals",
            headers=auth_headers_with_org,
            json={
                "contact_id": 99999,
                "title": "Invalid Deal",
            },
        )

        assert response.status_code == 404


class TestUpdateDeal:
    """Tests for update deal endpoint."""

    @pytest.mark.asyncio
    async def test_update_deal_title(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can update deal title."""
        response = await client.patch(
            f"/api/v1/deals/{test_deal.id}",
            headers=auth_headers_with_org,
            json={"title": "Updated Deal Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Deal Title"

    @pytest.mark.asyncio
    async def test_update_deal_status_to_won(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can update deal status to won with positive amount."""
        response = await client.patch(
            f"/api/v1/deals/{test_deal.id}",
            headers=auth_headers_with_org,
            json={"status": "won"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "won"

    @pytest.mark.asyncio
    async def test_update_deal_stage_forward(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can move deal stage forward."""
        response = await client.patch(
            f"/api/v1/deals/{test_deal.id}",
            headers=auth_headers_with_org,
            json={"stage": "proposal"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "proposal"

    @pytest.mark.asyncio
    async def test_cannot_win_deal_with_zero_amount(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_organization,
        test_user,
        test_contact,
    ):
        """Cannot close deal as won with zero amount."""
        # Create deal with zero amount
        deal = Deal(
            organization_id=test_organization.id,
            owner_id=test_user.id,
            contact_id=test_contact.id,
            title="Zero Amount Deal",
            amount=Decimal("0"),
            currency="USD",
            status=DealStatus.NEW,
            stage=DealStage.QUALIFICATION,
        )
        session.add(deal)
        await session.commit()
        await session.refresh(deal)

        response = await client.patch(
            f"/api/v1/deals/{deal.id}",
            headers=auth_headers_with_org,
            json={"status": "won"},
        )

        assert response.status_code == 400


class TestDeleteDeal:
    """Tests for delete deal endpoint."""

    @pytest.mark.asyncio
    async def test_delete_deal_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_organization,
        test_user,
        test_contact,
    ):
        """Can delete a deal."""
        # Create deal for deletion
        deal = Deal(
            organization_id=test_organization.id,
            owner_id=test_user.id,
            contact_id=test_contact.id,
            title="To Delete",
            amount=Decimal("1000"),
            currency="USD",
            status=DealStatus.NEW,
            stage=DealStage.QUALIFICATION,
        )
        session.add(deal)
        await session.commit()
        await session.refresh(deal)

        response = await client.delete(
            f"/api/v1/deals/{deal.id}",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 204
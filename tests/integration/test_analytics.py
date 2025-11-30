import pytest
from decimal import Decimal
from httpx import AsyncClient

from app.models import Deal
from app.models.enums import DealStage, DealStatus


class TestDealsSummary:
    """Tests for deals summary endpoint."""

    @pytest.mark.asyncio
    async def test_get_summary_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can get deals summary."""
        response = await client.get(
            "/api/v1/analytics/deals/summary",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 200
        data = response.json()

        assert "by_status" in data
        assert "average_won_amount" in data
        assert "new_deals_last_n_days" in data

        # Check by_status structure
        assert "new" in data["by_status"]
        assert "in_progress" in data["by_status"]
        assert "won" in data["by_status"]
        assert "lost" in data["by_status"]

        for status_data in data["by_status"].values():
            assert "count" in status_data
            assert "total_amount" in status_data

    @pytest.mark.asyncio
    async def test_get_summary_with_days_param(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can get deals summary with custom days parameter."""
        response = await client.get(
            "/api/v1/analytics/deals/summary",
            headers=auth_headers_with_org,
            params={"days": 7},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["new_deals_last_n_days"]["days"] == 7

    @pytest.mark.asyncio
    async def test_get_summary_unauthorized(self, client: AsyncClient):
        """Cannot get summary without auth."""
        response = await client.get("/api/v1/analytics/deals/summary")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_summary_counts_deals_correctly(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_organization,
        test_user,
        test_contact,
    ):
        """Summary counts deals by status correctly."""
        # Create deals with different statuses
        deals = [
            Deal(
                organization_id=test_organization.id,
                owner_id=test_user.id,
                contact_id=test_contact.id,
                title="Won Deal 1",
                amount=Decimal("1000"),
                currency="USD",
                status=DealStatus.WON,
                stage=DealStage.CLOSED,
            ),
            Deal(
                organization_id=test_organization.id,
                owner_id=test_user.id,
                contact_id=test_contact.id,
                title="Won Deal 2",
                amount=Decimal("2000"),
                currency="USD",
                status=DealStatus.WON,
                stage=DealStage.CLOSED,
            ),
            Deal(
                organization_id=test_organization.id,
                owner_id=test_user.id,
                contact_id=test_contact.id,
                title="Lost Deal",
                amount=Decimal("500"),
                currency="USD",
                status=DealStatus.LOST,
                stage=DealStage.NEGOTIATION,
            ),
        ]
        session.add_all(deals)
        await session.commit()

        response = await client.get(
            "/api/v1/analytics/deals/summary",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 200
        data = response.json()

        # At least 2 won deals
        assert data["by_status"]["won"]["count"] >= 2
        assert Decimal(str(data["by_status"]["won"]["total_amount"])) >= Decimal("3000")


class TestDealsFunnel:
    """Tests for deals funnel endpoint."""

    @pytest.mark.asyncio
    async def test_get_funnel_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal: Deal,
    ):
        """Can get deals funnel."""
        response = await client.get(
            "/api/v1/analytics/deals/funnel",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 200
        data = response.json()

        assert "stages" in data
        assert "stage_totals" in data
        assert "conversions" in data

    @pytest.mark.asyncio
    async def test_funnel_has_conversion_rates(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_organization,
        test_user,
        test_contact,
    ):
        """Funnel includes conversion rates between stages."""
        # Create deals at different stages
        deals = [
            Deal(
                organization_id=test_organization.id,
                owner_id=test_user.id,
                contact_id=test_contact.id,
                title="Qualification Deal",
                amount=Decimal("1000"),
                currency="USD",
                status=DealStatus.IN_PROGRESS,
                stage=DealStage.QUALIFICATION,
            ),
            Deal(
                organization_id=test_organization.id,
                owner_id=test_user.id,
                contact_id=test_contact.id,
                title="Proposal Deal",
                amount=Decimal("2000"),
                currency="USD",
                status=DealStatus.IN_PROGRESS,
                stage=DealStage.PROPOSAL,
            ),
            Deal(
                organization_id=test_organization.id,
                owner_id=test_user.id,
                contact_id=test_contact.id,
                title="Negotiation Deal",
                amount=Decimal("3000"),
                currency="USD",
                status=DealStatus.IN_PROGRESS,
                stage=DealStage.NEGOTIATION,
            ),
        ]
        session.add_all(deals)
        await session.commit()

        response = await client.get(
            "/api/v1/analytics/deals/funnel",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 200
        data = response.json()

        # Check conversions structure
        assert len(data["conversions"]) > 0

        for conversion in data["conversions"]:
            assert "from_stage" in conversion
            assert "to_stage" in conversion
            assert "from_count" in conversion
            assert "to_count" in conversion
            assert "conversion_rate" in conversion
            assert 0 <= conversion["conversion_rate"] <= 100

    @pytest.mark.asyncio
    async def test_funnel_unauthorized(self, client: AsyncClient):
        """Cannot get funnel without auth."""
        response = await client.get("/api/v1/analytics/deals/funnel")

        assert response.status_code == 401
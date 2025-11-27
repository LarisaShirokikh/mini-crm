"""Deal repository."""

from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.deal import Deal
from app.models.enums import DealStatus, DealStage
from app.repositories.base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    """Repository for Deal model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Deal, session)

    async def get_by_organization(
        self,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        status: list[DealStatus] | None = None,
        stage: DealStage | None = None,
        owner_id: int | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> list[Deal]:
        """Get deals for organization with filters."""
        query = select(Deal).where(Deal.organization_id == organization_id)

        if status:
            query = query.where(Deal.status.in_(status))

        if stage:
            query = query.where(Deal.stage == stage)

        if owner_id:
            query = query.where(Deal.owner_id == owner_id)

        if min_amount is not None:
            query = query.where(Deal.amount >= min_amount)

        if max_amount is not None:
            query = query.where(Deal.amount <= max_amount)

        # Sorting
        order_column = getattr(Deal, order_by, Deal.created_at)
        if order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_with_relations(self, deal_id: int) -> Deal | None:
        """Get deal with contact and owner loaded."""
        query = (
            select(Deal)
            .where(Deal.id == deal_id)
            .options(
                selectinload(Deal.contact),
                selectinload(Deal.owner),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_organization(
        self,
        organization_id: int,
        status: list[DealStatus] | None = None,
    ) -> int:
        """Count deals for organization."""
        query = select(func.count()).select_from(Deal).where(
            Deal.organization_id == organization_id
        )

        if status:
            query = query.where(Deal.status.in_(status))

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_summary_by_status(
        self,
        organization_id: int,
    ) -> list[dict]:
        """Get deal count and sum grouped by status."""
        query = (
            select(
                Deal.status,
                func.count(Deal.id).label("count"),
                func.sum(Deal.amount).label("total_amount"),
            )
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.status)
        )
        result = await self.session.execute(query)
        return [
            {
                "status": row.status,
                "count": row.count,
                "total_amount": row.total_amount or Decimal("0"),
            }
            for row in result.all()
        ]

    async def get_avg_won_amount(self, organization_id: int) -> Decimal:
        """Get average amount of won deals."""
        query = (
            select(func.avg(Deal.amount))
            .where(
                and_(
                    Deal.organization_id == organization_id,
                    Deal.status == DealStatus.WON,
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or Decimal("0")

    async def get_funnel_data(self, organization_id: int) -> list[dict]:
        """Get deals count by stage and status for funnel."""
        query = (
            select(
                Deal.stage,
                Deal.status,
                func.count(Deal.id).label("count"),
            )
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.stage, Deal.status)
        )
        result = await self.session.execute(query)
        return [
            {
                "stage": row.stage,
                "status": row.status,
                "count": row.count,
            }
            for row in result.all()
        ]
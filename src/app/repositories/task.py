"""Task repository."""

from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository for Task model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Task, session)

    async def get_by_deal(
        self,
        deal_id: int,
        *,
        only_open: bool = False,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Task]:
        """Get tasks for a deal with filters."""
        query = select(Task).where(Task.deal_id == deal_id)

        if only_open:
            query = query.where(Task.is_done == False)  # noqa: E712

        if due_before:
            query = query.where(Task.due_date <= due_before)

        if due_after:
            query = query.where(Task.due_date >= due_after)

        query = query.order_by(Task.due_date.asc().nullslast())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_organization(
        self,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        deal_id: int | None = None,
        only_open: bool = False,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Task]:
        """Get tasks for organization with filters."""
        from app.models.deal import Deal

        query = (
            select(Task)
            .join(Deal)
            .where(Deal.organization_id == organization_id)
        )

        if deal_id:
            query = query.where(Task.deal_id == deal_id)

        if only_open:
            query = query.where(Task.is_done == False)  # noqa: E712

        if due_before:
            query = query.where(Task.due_date <= due_before)

        if due_after:
            query = query.where(Task.due_date >= due_after)

        query = query.order_by(Task.due_date.asc().nullslast())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_deal(
        self,
        deal_id: int,
        only_open: bool = False,
    ) -> int:
        """Count tasks for a deal."""
        query = select(func.count()).select_from(Task).where(
            Task.deal_id == deal_id
        )

        if only_open:
            query = query.where(Task.is_done == False)  # noqa: E712

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def mark_done(self, task: Task) -> Task:
        """Mark task as completed."""
        return await self.update(task, is_done=True)

    async def mark_undone(self, task: Task) -> Task:
        """Mark task as not completed."""
        return await self.update(task, is_done=False)
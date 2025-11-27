"""Activity repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.models.enums import ActivityType
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    """Repository for Activity model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Activity, session)

    async def get_by_deal(
        self,
        deal_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Activity]:
        """Get activities for a deal (newest first)."""
        query = (
            select(Activity)
            .where(Activity.deal_id == deal_id)
            .options(selectinload(Activity.author))
            .order_by(Activity.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_comment(
        self,
        deal_id: int,
        author_id: int,
        text: str,
    ) -> Activity:
        """Create a comment activity."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.COMMENT,
            payload={"text": text},
        )

    async def create_status_changed(
        self,
        deal_id: int,
        author_id: int | None,
        old_status: str,
        new_status: str,
    ) -> Activity:
        """Create a status change activity."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.STATUS_CHANGED,
            payload={
                "old_status": old_status,
                "new_status": new_status,
            },
        )

    async def create_stage_changed(
        self,
        deal_id: int,
        author_id: int | None,
        old_stage: str,
        new_stage: str,
    ) -> Activity:
        """Create a stage change activity."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.STAGE_CHANGED,
            payload={
                "old_stage": old_stage,
                "new_stage": new_stage,
            },
        )

    async def create_task_created(
        self,
        deal_id: int,
        author_id: int,
        task_title: str,
    ) -> Activity:
        """Create a task created activity."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.TASK_CREATED,
            payload={"task_title": task_title},
        )

    async def create_task_completed(
        self,
        deal_id: int,
        author_id: int,
        task_title: str,
    ) -> Activity:
        """Create a task completed activity."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.TASK_COMPLETED,
            payload={"task_title": task_title},
        )
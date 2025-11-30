
from datetime import date

from app.core.exceptions import (
    DealNotFoundException,
    ForbiddenException,
    InvalidDueDateException,
    TaskNotFoundException,
)
from app.models.organization_member import OrganizationMember
from app.models.task import Task
from app.repositories.activity import ActivityRepository
from app.repositories.deal import DealRepository
from app.repositories.task import TaskRepository


class TaskService:

    def __init__(
        self,
        task_repo: TaskRepository,
        deal_repo: DealRepository,
        activity_repo: ActivityRepository,
    ) -> None:
        self.task_repo = task_repo
        self.deal_repo = deal_repo
        self.activity_repo = activity_repo

    async def get_tasks(
        self,
        organization_id: int,
        *,
        page: int = 1,
        page_size: int = 20,
        deal_id: int | None = None,
        only_open: bool = False,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Task]:
        skip = (page - 1) * page_size

        return await self.task_repo.get_by_organization(
            organization_id,
            skip=skip,
            limit=page_size,
            deal_id=deal_id,
            only_open=only_open,
            due_before=due_before,
            due_after=due_after,
        )

    async def get_task(
        self,
        task_id: int,
        organization_id: int,
    ) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException()

        # Verify task belongs to organization via deal
        deal = await self.deal_repo.get_by_id(task.deal_id)
        if not deal or deal.organization_id != organization_id:
            raise TaskNotFoundException()

        return task

    async def create_task(
        self,
        organization_id: int,
        membership: OrganizationMember,
        deal_id: int,
        title: str,
        description: str | None = None,
        due_date: date | None = None,
    ) -> Task:
        # Verify deal exists and belongs to organization
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise DealNotFoundException()

        # Members can only create tasks for their own deals
        if not membership.can_manage_all_entities():
            if deal.owner_id != membership.user_id:
                raise ForbiddenException(
                    message="Cannot create task for another user's deal"
                )

        # Validate due_date
        if due_date:
            self._validate_due_date(due_date)

        task = await self.task_repo.create(
            deal_id=deal_id,
            title=title,
            description=description,
            due_date=due_date,
        )

        # Create activity
        await self.activity_repo.create_task_created(
            deal_id=deal_id,
            author_id=membership.user_id,
            task_title=title,
        )

        return task

    async def update_task(
        self,
        task_id: int,
        organization_id: int,
        membership: OrganizationMember,
        **kwargs,
    ) -> Task:
        task = await self.get_task(task_id, organization_id)

        # Check permissions via deal
        deal = await self.deal_repo.get_by_id(task.deal_id)
        if not membership.can_manage_all_entities():
            if deal.owner_id != membership.user_id:
                raise ForbiddenException()

        # Validate due_date if provided
        new_due_date = kwargs.get("due_date")
        if new_due_date:
            self._validate_due_date(new_due_date)

        # Track completion for activity
        was_done = task.is_done
        updated_task = await self.task_repo.update(task, **kwargs)

        # Create activity if task was completed
        if not was_done and updated_task.is_done:
            await self.activity_repo.create_task_completed(
                deal_id=task.deal_id,
                author_id=membership.user_id,
                task_title=task.title,
            )

        return updated_task

    async def delete_task(
        self,
        task_id: int,
        organization_id: int,
        membership: OrganizationMember,
    ) -> None:
        task = await self.get_task(task_id, organization_id)

        # Check permissions via deal
        deal = await self.deal_repo.get_by_id(task.deal_id)
        if not membership.can_manage_all_entities():
            if deal.owner_id != membership.user_id:
                raise ForbiddenException()

        await self.task_repo.delete(task)

    def _validate_due_date(self, due_date: date) -> None:
        if due_date < date.today():
            raise InvalidDueDateException()
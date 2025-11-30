from datetime import date

from fastapi import APIRouter, Query

from app.api.v1.dependencies import CurrentMembership, DbSession, OrganizationId
from app.api.v1.schemas import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.repositories.activity import ActivityRepository
from app.repositories.deal import DealRepository
from app.repositories.task import TaskRepository
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_service(session: DbSession) -> TaskService:
    return TaskService(
        task_repo=TaskRepository(session),
        deal_repo=DealRepository(session),
        activity_repo=ActivityRepository(session),
    )


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    deal_id: int | None = None,
    only_open: bool = False,
    due_before: date | None = None,
    due_after: date | None = None,
) -> TaskListResponse:
    task_service = get_task_service(session)

    tasks = await task_service.get_tasks(
        organization_id=organization_id,
        page=page,
        page_size=page_size,
        deal_id=deal_id,
        only_open=only_open,
        due_before=due_before,
        due_after=due_after,
    )

    return TaskListResponse(
        items=tasks,
        total=len(tasks),
        page=page,
        page_size=page_size,
        pages=1,
    )


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> TaskResponse:
    task_service = get_task_service(session)

    task = await task_service.create_task(
        organization_id=organization_id,
        membership=membership,
        deal_id=data.deal_id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
    )

    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> TaskResponse:
    task_service = get_task_service(session)
    task = await task_service.get_task(task_id, organization_id)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> TaskResponse:
    task_service = get_task_service(session)

    update_data = data.model_dump(exclude_unset=True)
    task = await task_service.update_task(
        task_id=task_id,
        organization_id=organization_id,
        membership=membership,
        **update_data,
    )

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> None:
    task_service = get_task_service(session)

    await task_service.delete_task(
        task_id=task_id,
        organization_id=organization_id,
        membership=membership,
    )
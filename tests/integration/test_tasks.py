"""Integration tests for tasks endpoints."""

import pytest
from datetime import date, timedelta
from httpx import AsyncClient

from app.models import Task


class TestListTasks:
    """Tests for list tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_tasks_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_deal,
    ):
        """Can list tasks."""
        # Create a task
        task = Task(
            deal_id=test_deal.id,
            title="Test Task",
            is_done=False,
        )
        session.add(task)
        await session.commit()

        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_deal(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_deal,
    ):
        """Can filter tasks by deal."""
        task = Task(
            deal_id=test_deal.id,
            title="Deal Task",
            is_done=False,
        )
        session.add(task)
        await session.commit()

        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers_with_org,
            params={"deal_id": test_deal.id},
        )

        assert response.status_code == 200
        data = response.json()

        for item in data["items"]:
            assert item["deal_id"] == test_deal.id

    @pytest.mark.asyncio
    async def test_list_tasks_only_open(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_deal,
    ):
        """Can filter only open tasks."""
        # Create open task
        open_task = Task(
            deal_id=test_deal.id,
            title="Open Task",
            is_done=False,
        )
        # Create closed task
        closed_task = Task(
            deal_id=test_deal.id,
            title="Closed Task",
            is_done=True,
        )
        session.add_all([open_task, closed_task])
        await session.commit()

        response = await client.get(
            "/api/v1/tasks",
            headers=auth_headers_with_org,
            params={"only_open": True},
        )

        assert response.status_code == 200
        data = response.json()

        for item in data["items"]:
            assert item["is_done"] is False


class TestCreateTask:
    """Tests for create task endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal,
    ):
        """Can create a task."""
        response = await client.post(
            "/api/v1/tasks",
            headers=auth_headers_with_org,
            json={
                "deal_id": test_deal.id,
                "title": "New Task",
                "description": "Task description",
                "due_date": str(date.today() + timedelta(days=7)),
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["is_done"] is False

    @pytest.mark.asyncio
    async def test_create_task_minimal(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal,
    ):
        """Can create task with only required fields."""
        response = await client.post(
            "/api/v1/tasks",
            headers=auth_headers_with_org,
            json={
                "deal_id": test_deal.id,
                "title": "Minimal Task",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"

    @pytest.mark.asyncio
    async def test_create_task_past_due_date(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_deal,
    ):
        """Cannot create task with past due date."""
        response = await client.post(
            "/api/v1/tasks",
            headers=auth_headers_with_org,
            json={
                "deal_id": test_deal.id,
                "title": "Past Task",
                "due_date": str(date.today() - timedelta(days=1)),
            },
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_task_invalid_deal(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_member,
    ):
        """Cannot create task for nonexistent deal."""
        response = await client.post(
            "/api/v1/tasks",
            headers=auth_headers_with_org,
            json={
                "deal_id": 99999,
                "title": "Invalid Task",
            },
        )

        assert response.status_code == 404


class TestUpdateTask:
    """Tests for update task endpoint."""

    @pytest.mark.asyncio
    async def test_update_task_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_deal,
    ):
        """Can update a task."""
        task = Task(
            deal_id=test_deal.id,
            title="Original Title",
            is_done=False,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers_with_org,
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_mark_task_done(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_deal,
    ):
        """Can mark task as done."""
        task = Task(
            deal_id=test_deal.id,
            title="Task to Complete",
            is_done=False,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        response = await client.patch(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers_with_org,
            json={"is_done": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_done"] is True


class TestDeleteTask:
    """Tests for delete task endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_deal,
    ):
        """Can delete a task."""
        task = Task(
            deal_id=test_deal.id,
            title="Task to Delete",
            is_done=False,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        response = await client.delete(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 204
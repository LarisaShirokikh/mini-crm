import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import InvalidDueDateException
from app.services.task import TaskService


class TestTaskDueDateValidation:
    """Tests for task due date validation."""

    @pytest.fixture
    def task_service(self):
        """Create task service with mocked repos."""
        return TaskService(
            task_repo=AsyncMock(),
            deal_repo=AsyncMock(),
            activity_repo=AsyncMock(),
        )

    def test_due_date_today_is_valid(self, task_service):
        """Due date of today is valid."""
        # Should not raise
        task_service._validate_due_date(date.today())

    def test_due_date_tomorrow_is_valid(self, task_service):
        """Due date of tomorrow is valid."""
        # Should not raise
        task_service._validate_due_date(date.today() + timedelta(days=1))

    def test_due_date_future_is_valid(self, task_service):
        """Due date in the future is valid."""
        # Should not raise
        task_service._validate_due_date(date.today() + timedelta(days=30))

    def test_due_date_yesterday_is_invalid(self, task_service):
        """Due date of yesterday is invalid."""
        with pytest.raises(InvalidDueDateException):
            task_service._validate_due_date(date.today() - timedelta(days=1))

    def test_due_date_past_is_invalid(self, task_service):
        """Due date in the past is invalid."""
        with pytest.raises(InvalidDueDateException):
            task_service._validate_due_date(date.today() - timedelta(days=30))
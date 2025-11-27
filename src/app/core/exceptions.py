from typing import Any


class AppException(Exception):
    """Base exception for application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to API response format."""
        result: dict[str, Any] = {
            "error": {
                "code": self.error_code,
                "message": self.message,
            }
        }
        if self.details:
            result["error"]["details"] = self.details
        return result


class UnauthorizedException(AppException):
    """User is not authenticated."""

    status_code = 401
    error_code = "UNAUTHORIZED"
    message = "Authentication required"


class InvalidCredentialsException(AppException):
    """Invalid email or password."""

    status_code = 401
    error_code = "INVALID_CREDENTIALS"
    message = "Invalid email or password"


class InvalidTokenException(AppException):
    """JWT token is invalid or expired."""

    status_code = 401
    error_code = "INVALID_TOKEN"
    message = "Invalid or expired token"


class ForbiddenException(AppException):
    """User doesn't have permission for this action."""

    status_code = 403
    error_code = "FORBIDDEN"
    message = "You don't have permission to perform this action"


class OrganizationAccessDeniedException(AppException):
    """User doesn't have access to this organization."""

    status_code = 403
    error_code = "ORGANIZATION_ACCESS_DENIED"
    message = "Access to this organization is denied"


class NotFoundException(AppException):
    """Resource not found."""

    status_code = 404
    error_code = "NOT_FOUND"
    message = "Resource not found"


class UserNotFoundException(NotFoundException):
    """User not found."""

    error_code = "USER_NOT_FOUND"
    message = "User not found"


class OrganizationNotFoundException(NotFoundException):
    """Organization not found."""

    error_code = "ORGANIZATION_NOT_FOUND"
    message = "Organization not found"


class ContactNotFoundException(NotFoundException):
    """Contact not found."""

    error_code = "CONTACT_NOT_FOUND"
    message = "Contact not found"


class DealNotFoundException(NotFoundException):
    """Deal not found."""

    error_code = "DEAL_NOT_FOUND"
    message = "Deal not found"


class TaskNotFoundException(NotFoundException):
    """Task not found."""

    error_code = "TASK_NOT_FOUND"
    message = "Task not found"


class ValidationException(AppException):
    """Request validation failed."""

    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "Validation error"


class InvalidDealAmountException(ValidationException):
    """Deal amount is invalid for the requested status."""

    error_code = "INVALID_DEAL_AMOUNT"
    message = "Cannot close deal as 'won' with amount <= 0"


class InvalidDueDateException(ValidationException):
    """Due date cannot be in the past."""

    error_code = "INVALID_DUE_DATE"
    message = "Due date cannot be in the past"


class InvalidStageTransitionException(ValidationException):
    """Stage transition is not allowed."""

    error_code = "INVALID_STAGE_TRANSITION"
    message = "Stage rollback is not allowed for your role"


class CrossOrganizationException(ValidationException):
    """Attempt to link entities from different organizations."""

    error_code = "CROSS_ORGANIZATION_ERROR"
    message = "Cannot link entities from different organizations"



class ConflictException(AppException):
    """Resource conflict."""

    status_code = 409
    error_code = "CONFLICT"
    message = "Resource conflict"


class EmailAlreadyExistsException(ConflictException):
    """Email is already registered."""

    error_code = "EMAIL_ALREADY_EXISTS"
    message = "Email is already registered"


class ContactHasDealsException(ConflictException):
    """Cannot delete contact with existing deals."""

    error_code = "CONTACT_HAS_DEALS"
    message = "Cannot delete contact with existing deals"


class MemberAlreadyExistsException(ConflictException):
    """User is already a member of this organization."""

    error_code = "MEMBER_ALREADY_EXISTS"
    message = "User is already a member of this organization"
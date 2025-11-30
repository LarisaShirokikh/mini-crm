"""API schemas module."""

from app.api.v1.schemas.activity import (
    ActivityCreate,
    ActivityDetailResponse,
    ActivityListResponse,
    ActivityResponse,
)
from app.api.v1.schemas.analytics import (
    DealsSummaryResponse,
    FunnelResponse,
)
from app.api.v1.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.api.v1.schemas.base import (
    BaseSchema,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.api.v1.schemas.contact import (
    ContactCreate,
    ContactDetailResponse,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
)
from app.api.v1.schemas.deal import (
    DealCreate,
    DealDetailResponse,
    DealListResponse,
    DealResponse,
    DealUpdate,
)
from app.api.v1.schemas.organization import (
    AddMemberRequest,
    MemberResponse,
    OrganizationResponse,
    OrganizationWithRoleResponse,
    UpdateMemberRoleRequest,
)
from app.api.v1.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.api.v1.schemas.user import (
    UserBriefResponse,
    UserResponse,
)

__all__ = [
    # Base
    "BaseSchema",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationParams",
    # Auth
    "LoginRequest",
    "RefreshRequest",
    "RegisterRequest",
    "RegisterResponse",
    "TokenResponse",
    # User
    "UserBriefResponse",
    "UserResponse",
    # Organization
    "AddMemberRequest",
    "MemberResponse",
    "OrganizationResponse",
    "OrganizationWithRoleResponse",
    "UpdateMemberRoleRequest",
    # Contact
    "ContactCreate",
    "ContactDetailResponse",
    "ContactListResponse",
    "ContactResponse",
    "ContactUpdate",
    # Deal
    "DealCreate",
    "DealDetailResponse",
    "DealListResponse",
    "DealResponse",
    "DealUpdate",
    # Task
    "TaskCreate",
    "TaskListResponse",
    "TaskResponse",
    "TaskUpdate",
    # Activity
    "ActivityCreate",
    "ActivityDetailResponse",
    "ActivityListResponse",
    "ActivityResponse",
    # Analytics
    "DealsSummaryResponse",
    "FunnelResponse",
]
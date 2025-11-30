from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    OrganizationAccessDeniedException,
    UnauthorizedException,
)
from app.core.security import verify_access_token
from app.db.session import get_session
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.repositories.organization import OrganizationMemberRepository
from app.repositories.user import UserRepository


async def get_current_user(
        authorization: Annotated[str | None, Header()] = None,
        session: AsyncSession = Depends(get_session),
) -> User:
    """Get current authenticated user from JWT token."""
    if not authorization:
        raise UnauthorizedException()

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(message="Invalid authorization header")

    token = parts[1]
    payload = verify_access_token(token)

    user_id = int(payload["sub"])
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException(message="User not found")

    return user


async def get_organization_id_header(
        x_organization_id: Annotated[int | None, Header()] = None,
) -> int | None:
    """Get organization ID from header (without validation)."""
    return x_organization_id


async def get_current_membership(
        current_user: Annotated[User, Depends(get_current_user)],
        organization_id: Annotated[int | None, Depends(get_organization_id_header)],
        session: AsyncSession = Depends(get_session),
) -> OrganizationMember:
    """Get current user's membership in the organization.

    Auth check (401) happens first via get_current_user dependency.
    Then org access check (403) happens here.
    """
    # Check org header AFTER auth is verified
    if not organization_id:
        raise OrganizationAccessDeniedException(
            message="X-Organization-Id header is required"
        )

    member_repo = OrganizationMemberRepository(session)
    membership = await member_repo.get_membership(
        organization_id,
        current_user.id
    )

    if not membership:
        raise OrganizationAccessDeniedException()

    return membership


# For endpoints that only need org_id (after auth check)
async def get_organization_id(
        current_user: Annotated[User, Depends(get_current_user)],
        organization_id: Annotated[int | None, Depends(get_organization_id_header)],
) -> int:
    """Get organization ID, ensuring user is authenticated first."""
    if not organization_id:
        raise OrganizationAccessDeniedException(
            message="X-Organization-Id header is required"
        )
    return organization_id


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
OrganizationId = Annotated[int, Depends(get_organization_id)]
CurrentMembership = Annotated[OrganizationMember, Depends(get_current_membership)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
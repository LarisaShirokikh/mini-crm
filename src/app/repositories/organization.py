from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.enums import OrganizationRole
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for Organization model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Organization, session)

    async def get_user_organizations(self, user_id: int) -> list[Organization]:
        """Get all organizations where user is a member."""
        query = (
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
            .options(selectinload(Organization.members))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_with_members(self, org_id: int) -> Organization | None:
        """Get organization with members loaded."""
        query = (
            select(Organization)
            .where(Organization.id == org_id)
            .options(selectinload(Organization.members))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    """Repository for OrganizationMember model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(OrganizationMember, session)

    async def get_membership(
        self,
        organization_id: int,
        user_id: int,
    ) -> OrganizationMember | None:
        """Get user's membership in an organization."""
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def is_member(self, organization_id: int, user_id: int) -> bool:
        """Check if user is a member of organization."""
        membership = await self.get_membership(organization_id, user_id)
        return membership is not None

    async def get_user_role(
        self,
        organization_id: int,
        user_id: int,
    ) -> OrganizationRole | None:
        """Get user's role in organization."""
        membership = await self.get_membership(organization_id, user_id)
        return membership.role if membership else None

    async def add_member(
        self,
        organization_id: int,
        user_id: int,
        role: OrganizationRole = OrganizationRole.MEMBER,
    ) -> OrganizationMember:
        """Add a user to organization."""
        return await self.create(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )
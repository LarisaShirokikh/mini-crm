from app.core.exceptions import (
    ForbiddenException,
    MemberAlreadyExistsException,
    OrganizationNotFoundException,
    UserNotFoundException,
)
from app.models.enums import OrganizationRole
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.repositories.organization import OrganizationMemberRepository, OrganizationRepository
from app.repositories.user import UserRepository


class OrganizationService:
   
    def __init__(
        self,
        org_repo: OrganizationRepository,
        member_repo: OrganizationMemberRepository,
        user_repo: UserRepository,
    ) -> None:
        self.org_repo = org_repo
        self.member_repo = member_repo
        self.user_repo = user_repo

    async def get_user_organizations(self, user_id: int) -> list[Organization]:
        
        return await self.org_repo.get_user_organizations(user_id)

    async def get_organization(self, org_id: int, user_id: int) -> Organization:
        
        membership = await self.member_repo.get_membership(org_id, user_id)

        if not membership:
            raise OrganizationNotFoundException()

        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise OrganizationNotFoundException()

        return org

    async def get_user_membership(
        self,
        organization_id: int,
        user_id: int,
    ) -> OrganizationMember:
        
        membership = await self.member_repo.get_membership(organization_id, user_id)

        if not membership:
            raise OrganizationNotFoundException()

        return membership

    async def add_member(
        self,
        organization_id: int,
        user_email: str,
        role: OrganizationRole,
        current_user_id: int,
    ) -> OrganizationMember:
        
        # Check current user's permissions
        current_membership = await self.member_repo.get_membership(
            organization_id, current_user_id
        )

        if not current_membership or not current_membership.can_manage_organization():
            raise ForbiddenException()

        # Find user to add
        user = await self.user_repo.get_by_email(user_email)
        if not user:
            raise UserNotFoundException(message=f"User with email {user_email} not found")

        # Check if already a member
        existing = await self.member_repo.get_membership(organization_id, user.id)
        if existing:
            raise MemberAlreadyExistsException()

        # Add member
        return await self.member_repo.add_member(
            organization_id=organization_id,
            user_id=user.id,
            role=role,
        )

    async def update_member_role(
        self,
        organization_id: int,
        target_user_id: int,
        new_role: OrganizationRole,
        current_user_id: int,
    ) -> OrganizationMember:
        
        # Check current user's permissions
        current_membership = await self.member_repo.get_membership(
            organization_id, current_user_id
        )

        if not current_membership or not current_membership.can_manage_organization():
            raise ForbiddenException()

        # Cannot change own role
        if target_user_id == current_user_id:
            raise ForbiddenException(message="Cannot change your own role")

        # Get target membership
        target_membership = await self.member_repo.get_membership(
            organization_id, target_user_id
        )

        if not target_membership:
            raise UserNotFoundException()

        # Only owner can change another owner/admin
        if (
            target_membership.role in (OrganizationRole.OWNER, OrganizationRole.ADMIN)
            and current_membership.role != OrganizationRole.OWNER
        ):
            raise ForbiddenException()

        return await self.member_repo.update(target_membership, role=new_role)

    async def remove_member(
        self,
        organization_id: int,
        target_user_id: int,
        current_user_id: int,
    ) -> None:
        
        current_membership = await self.member_repo.get_membership(
            organization_id, current_user_id
        )

        if not current_membership or not current_membership.can_manage_organization():
            raise ForbiddenException()

        # Cannot remove yourself
        if target_user_id == current_user_id:
            raise ForbiddenException(message="Cannot remove yourself")

        target_membership = await self.member_repo.get_membership(
            organization_id, target_user_id
        )

        if not target_membership:
            raise UserNotFoundException()

        # Cannot remove owner
        if target_membership.role == OrganizationRole.OWNER:
            raise ForbiddenException(message="Cannot remove organization owner")

        await self.member_repo.delete(target_membership)
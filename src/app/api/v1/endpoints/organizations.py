from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import CurrentUser, DbSession
from app.api.v1.schemas import (
    AddMemberRequest,
    MemberResponse,
    OrganizationWithRoleResponse,
    UpdateMemberRoleRequest,
)
from app.repositories.organization import (
    OrganizationMemberRepository,
    OrganizationRepository,
)
from app.repositories.user import UserRepository
from app.services.organization import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


def get_org_service(session: DbSession) -> OrganizationService:
    return OrganizationService(
        org_repo=OrganizationRepository(session),
        member_repo=OrganizationMemberRepository(session),
        user_repo=UserRepository(session),
    )


@router.get("/me", response_model=list[OrganizationWithRoleResponse])
async def get_my_organizations(
    current_user: CurrentUser,
    session: DbSession,
) -> list[OrganizationWithRoleResponse]:
    org_service = get_org_service(session)
    organizations = await org_service.get_user_organizations(current_user.id)

    result = []
    member_repo = OrganizationMemberRepository(session)

    for org in organizations:
        membership = await member_repo.get_membership(org.id, current_user.id)
        result.append(
            OrganizationWithRoleResponse(
                id=org.id,
                name=org.name,
                created_at=org.created_at,
                role=membership.role,
            )
        )

    return result


@router.post("/{organization_id}/members", response_model=MemberResponse)
async def add_member(
    organization_id: int,
    data: AddMemberRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> MemberResponse:
    org_service = get_org_service(session)

    membership = await org_service.add_member(
        organization_id=organization_id,
        user_email=data.email,
        role=data.role,
        current_user_id=current_user.id,
    )

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(membership.user_id)

    return MemberResponse(
        id=membership.id,
        user_id=membership.user_id,
        user_name=user.name,
        user_email=user.email,
        role=membership.role,
    )


@router.patch("/{organization_id}/members/{user_id}", response_model=MemberResponse)
async def update_member_role(
    organization_id: int,
    user_id: int,
    data: UpdateMemberRoleRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> MemberResponse:
    org_service = get_org_service(session)

    membership = await org_service.update_member_role(
        organization_id=organization_id,
        target_user_id=user_id,
        new_role=data.role,
        current_user_id=current_user.id,
    )

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(membership.user_id)

    return MemberResponse(
        id=membership.id,
        user_id=membership.user_id,
        user_name=user.name,
        user_email=user.email,
        role=membership.role,
    )


@router.delete("/{organization_id}/members/{user_id}", status_code=204)
async def remove_member(
    organization_id: int,
    user_id: int,
    current_user: CurrentUser,
    session: DbSession,
) -> None:
    org_service = get_org_service(session)

    await org_service.remove_member(
        organization_id=organization_id,
        target_user_id=user_id,
        current_user_id=current_user.id,
    )
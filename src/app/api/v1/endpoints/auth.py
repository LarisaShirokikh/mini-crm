from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.db.session import get_session
from app.repositories.organization import (
    OrganizationMemberRepository,
    OrganizationRepository,
)
from app.repositories.user import UserRepository
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(
        session: AsyncSession = Depends(get_session)
) -> AuthService:
    return AuthService(
        user_repo=UserRepository(session),
        org_repo=OrganizationRepository(session),
        member_repo=OrganizationMemberRepository(session),
    )


@router.post("/register", response_model=RegisterResponse)
async def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    user, organization, tokens = await auth_service.register(
        email=data.email,
        password=data.password,
        name=data.name,
        organization_name=data.organization_name,
    )

    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        organization_id=organization.id,
        organization_name=organization.name,
        **tokens,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    user, tokens = await auth_service.login(
        email=data.email,
        password=data.password,
    )

    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    tokens = await auth_service.refresh_tokens(data.refresh_token)
    return TokenResponse(**tokens)
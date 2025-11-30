from app.core.exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.models.enums import OrganizationRole
from app.models.organization import Organization
from app.models.user import User
from app.repositories.organization import OrganizationMemberRepository, OrganizationRepository
from app.repositories.user import UserRepository


class AuthService:

    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        member_repo: OrganizationMemberRepository,
    ) -> None:
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.member_repo = member_repo

    async def register(
        self,
        email: str,
        password: str,
        name: str,
        organization_name: str,
    ) -> tuple[User, Organization, dict[str, str]]:
        
        # Check if email exists
        if await self.user_repo.email_exists(email):
            raise EmailAlreadyExistsException()

        # Create user
        user = await self.user_repo.create(
            email=email,
            hashed_password=hash_password(password),
            name=name,
        )

        # Create organization
        organization = await self.org_repo.create(name=organization_name)

        # Add user as owner
        await self.member_repo.add_member(
            organization_id=organization.id,
            user_id=user.id,
            role=OrganizationRole.OWNER,
        )

        # Generate tokens
        tokens = self._generate_tokens(user.id)

        return user, organization, tokens

    async def login(
        self,
        email: str,
        password: str,
    ) -> tuple[User, dict[str, str]]:
       
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        tokens = self._generate_tokens(user.id)

        return user, tokens

    async def refresh_tokens(self, refresh_token: str) -> dict[str, str]:
        payload = verify_refresh_token(refresh_token)
        user_id = int(payload["sub"])

        return self._generate_tokens(user_id)

    def _generate_tokens(self, user_id: int) -> dict[str, str]:
        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id),
            "token_type": "bearer",
        }
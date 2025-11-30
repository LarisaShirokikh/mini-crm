import asyncio
from collections.abc import AsyncGenerator
from typing import Generator
from decimal import Decimal
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.core.config import settings
from app.core.security import hash_password, create_access_token
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models import Organization, OrganizationMember, User, Contact, Deal
from app.models.enums import OrganizationRole, DealStatus, DealStage

# Test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/mini_crm", "/mini_crm_test")

# Create engine with NullPool to avoid connection issues
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create tables before tests, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_tables():
    """Clean up all tables before each test."""
    yield
    # Cleanup after test
    async with TestSessionLocal() as session:
        # Delete in correct order due to foreign keys
        await session.execute(text("DELETE FROM activities"))
        await session.execute(text("DELETE FROM tasks"))
        await session.execute(text("DELETE FROM deals"))
        await session.execute(text("DELETE FROM contacts"))
        await session.execute(text("DELETE FROM organization_members"))
        await session.execute(text("DELETE FROM organizations"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with TestSessionLocal() as session:
        yield session


async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override for get_session."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(session: AsyncSession) -> User:
    """Create a test user with unique email."""
    unique_id = uuid.uuid4().hex[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        hashed_password=hash_password("password123"),
        name="Test User",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_organization(session: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(name="Test Organization")
    session.add(org)
    await session.commit()
    await session.refresh(org)
    return org


@pytest_asyncio.fixture
async def test_member(
        session: AsyncSession,
        test_user: User,
        test_organization: Organization,
) -> OrganizationMember:
    """Create a test organization member (owner)."""
    member = OrganizationMember(
        organization_id=test_organization.id,
        user_id=test_user.id,
        role=OrganizationRole.OWNER,
    )
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return member


@pytest_asyncio.fixture
async def test_contact(
        session: AsyncSession,
        test_organization: Organization,
        test_user: User,
) -> Contact:
    """Create a test contact."""
    contact = Contact(
        organization_id=test_organization.id,
        owner_id=test_user.id,
        name="John Doe",
        email="john@example.com",
        phone="+123456789",
    )
    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    return contact


@pytest_asyncio.fixture
async def test_deal(
        session: AsyncSession,
        test_organization: Organization,
        test_user: User,
        test_contact: Contact,
) -> Deal:
    """Create a test deal."""
    deal = Deal(
        organization_id=test_organization.id,
        owner_id=test_user.id,
        contact_id=test_contact.id,
        title="Test Deal",
        amount=Decimal("10000.00"),
        currency="USD",
        status=DealStatus.NEW,
        stage=DealStage.QUALIFICATION,
    )
    session.add(deal)
    await session.commit()
    await session.refresh(deal)
    return deal


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    """Get authorization headers for test user."""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_with_org(
        auth_headers: dict[str, str],
        test_organization: Organization,
        test_member: OrganizationMember,  # Ensure member exists
) -> dict[str, str]:
    """Get authorization headers with organization context."""
    return {
        **auth_headers,
        "X-Organization-Id": str(test_organization.id),
    }
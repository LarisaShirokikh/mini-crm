from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    """Repository for Contact model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Contact, session)

    async def get_by_organization(
        self,
        organization_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        owner_id: int | None = None,
    ) -> list[Contact]:
        """Get contacts for organization with filters."""
        query = select(Contact).where(
            Contact.organization_id == organization_id
        )

        if search:
            search_filter = or_(
                Contact.name.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        if owner_id:
            query = query.where(Contact.owner_id == owner_id)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_organization(
        self,
        organization_id: int,
        search: str | None = None,
        owner_id: int | None = None,
    ) -> int:
        """Count contacts for organization."""
        query = select(func.count()).select_from(Contact).where(
            Contact.organization_id == organization_id
        )

        if search:
            search_filter = or_(
                Contact.name.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        if owner_id:
            query = query.where(Contact.owner_id == owner_id)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def has_deals(self, contact_id: int) -> bool:
        """Check if contact has any deals."""
        from app.models.deal import Deal
        query = select(func.count()).select_from(Deal).where(
            Deal.contact_id == contact_id
        )
        result = await self.session.execute(query)
        return (result.scalar() or 0) > 0
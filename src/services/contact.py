from app.core.exceptions import (
    ContactHasDealsException,
    ContactNotFoundException,
    ForbiddenException,
)
from app.models.contact import Contact
from app.models.organization_member import OrganizationMember
from app.repositories.contact import ContactRepository


class ContactService:
    

    def __init__(self, contact_repo: ContactRepository) -> None:
        self.contact_repo = contact_repo

    async def get_contacts(
        self,
        organization_id: int,
        membership: OrganizationMember,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        owner_id: int | None = None,
    ) -> tuple[list[Contact], int]:
        
        # Members can only filter by owner if it's themselves
        if not membership.can_manage_all_entities() and owner_id:
            if owner_id != membership.user_id:
                owner_id = membership.user_id

        skip = (page - 1) * page_size

        contacts = await self.contact_repo.get_by_organization(
            organization_id,
            skip=skip,
            limit=page_size,
            search=search,
            owner_id=owner_id,
        )

        total = await self.contact_repo.count_by_organization(
            organization_id,
            search=search,
            owner_id=owner_id,
        )

        return contacts, total

    async def get_contact(
        self,
        contact_id: int,
        organization_id: int,
    ) -> Contact:
        
        contact = await self.contact_repo.get_by_id(contact_id)

        if not contact or contact.organization_id != organization_id:
            raise ContactNotFoundException()

        return contact

    async def create_contact(
        self,
        organization_id: int,
        owner_id: int,
        name: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> Contact:
       
        return await self.contact_repo.create(
            organization_id=organization_id,
            owner_id=owner_id,
            name=name,
            email=email,
            phone=phone,
        )

    async def update_contact(
        self,
        contact_id: int,
        organization_id: int,
        membership: OrganizationMember,
        **kwargs,
    ) -> Contact:
      
        contact = await self.get_contact(contact_id, organization_id)

        # Check permissions
        if not membership.can_manage_all_entities():
            if contact.owner_id != membership.user_id:
                raise ForbiddenException()

        return await self.contact_repo.update(contact, **kwargs)

    async def delete_contact(
        self,
        contact_id: int,
        organization_id: int,
        membership: OrganizationMember,
    ) -> None:
       
        contact = await self.get_contact(contact_id, organization_id)

        # Check permissions
        if not membership.can_manage_all_entities():
            if contact.owner_id != membership.user_id:
                raise ForbiddenException()

        # Check for existing deals
        if await self.contact_repo.has_deals(contact_id):
            raise ContactHasDealsException()

        await self.contact_repo.delete(contact)
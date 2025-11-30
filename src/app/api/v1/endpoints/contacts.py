from fastapi import APIRouter, Query

from app.api.v1.dependencies import CurrentMembership, DbSession, OrganizationId
from app.api.v1.schemas import (
    ContactCreate,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
)
from app.repositories.contact import ContactRepository
from app.services.contact import ContactService

router = APIRouter(prefix="/contacts", tags=["Contacts"])


def get_contact_service(session: DbSession) -> ContactService:
    return ContactService(contact_repo=ContactRepository(session))


@router.get("", response_model=ContactListResponse)
async def list_contacts(
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    owner_id: int | None = None,
) -> ContactListResponse:
    contact_service = get_contact_service(session)

    contacts, total = await contact_service.get_contacts(
        organization_id=organization_id,
        membership=membership,
        page=page,
        page_size=page_size,
        search=search,
        owner_id=owner_id,
    )

    pages = (total + page_size - 1) // page_size

    return ContactListResponse(
        items=contacts,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("", response_model=ContactResponse, status_code=201)
async def create_contact(
    data: ContactCreate,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> ContactResponse:
    contact_service = get_contact_service(session)

    contact = await contact_service.create_contact(
        organization_id=organization_id,
        owner_id=membership.user_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
    )

    return ContactResponse.model_validate(contact)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> ContactResponse:
    contact_service = get_contact_service(session)
    contact = await contact_service.get_contact(contact_id, organization_id)
    return ContactResponse.model_validate(contact)


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    data: ContactUpdate,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> ContactResponse:
    contact_service = get_contact_service(session)

    update_data = data.model_dump(exclude_unset=True)
    contact = await contact_service.update_contact(
        contact_id=contact_id,
        organization_id=organization_id,
        membership=membership,
        **update_data,
    )

    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    organization_id: OrganizationId,
    membership: CurrentMembership,
    session: DbSession,
) -> None:
    contact_service = get_contact_service(session)

    await contact_service.delete_contact(
        contact_id=contact_id,
        organization_id=organization_id,
        membership=membership,
    )
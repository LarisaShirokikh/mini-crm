"""Integration tests for contacts endpoints."""

import pytest
from httpx import AsyncClient

from app.models import Contact


class TestListContacts:
    """Tests for list contacts endpoint."""

    @pytest.mark.asyncio
    async def test_list_contacts_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_contact: Contact,
    ):
        """Can list contacts."""
        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_contacts_unauthorized(self, client: AsyncClient):
        """Cannot list contacts without auth."""
        response = await client.get("/api/v1/contacts")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_contacts_no_org_header(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Cannot list contacts without organization header."""
        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers,
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_contacts_with_search(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_contact: Contact,
    ):
        """Can search contacts by name."""
        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers_with_org,
            params={"search": "John"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1


class TestCreateContact:
    """Tests for create contact endpoint."""

    @pytest.mark.asyncio
    async def test_create_contact_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_member,
    ):
        """Can create a contact."""
        response = await client.post(
            "/api/v1/contacts",
            headers=auth_headers_with_org,
            json={
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+987654321",
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Jane Smith"
        assert data["email"] == "jane@example.com"
        assert data["phone"] == "+987654321"

    @pytest.mark.asyncio
    async def test_create_contact_minimal(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_member,
    ):
        """Can create contact with only name."""
        response = await client.post(
            "/api/v1/contacts",
            headers=auth_headers_with_org,
            json={"name": "Minimal Contact"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Contact"

    @pytest.mark.asyncio
    async def test_create_contact_empty_name(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_member,
    ):
        """Cannot create contact without name."""
        response = await client.post(
            "/api/v1/contacts",
            headers=auth_headers_with_org,
            json={"name": ""},
        )

        assert response.status_code == 422


class TestGetContact:
    """Tests for get contact endpoint."""

    @pytest.mark.asyncio
    async def test_get_contact_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_contact: Contact,
    ):
        """Can get a contact by ID."""
        response = await client.get(
            f"/api/v1/contacts/{test_contact.id}",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_contact.id
        assert data["name"] == test_contact.name

    @pytest.mark.asyncio
    async def test_get_contact_not_found(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_member,
    ):
        """Returns 404 for nonexistent contact."""
        response = await client.get(
            "/api/v1/contacts/99999",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 404


class TestUpdateContact:
    """Tests for update contact endpoint."""

    @pytest.mark.asyncio
    async def test_update_contact_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_contact: Contact,
    ):
        """Can update a contact."""
        response = await client.patch(
            f"/api/v1/contacts/{test_contact.id}",
            headers=auth_headers_with_org,
            json={"name": "Updated Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_contact_partial(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_contact: Contact,
    ):
        """Partial update preserves other fields."""
        original_email = test_contact.email

        response = await client.patch(
            f"/api/v1/contacts/{test_contact.id}",
            headers=auth_headers_with_org,
            json={"phone": "+111222333"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+111222333"
        assert data["email"] == original_email


class TestDeleteContact:
    """Tests for delete contact endpoint."""

    @pytest.mark.asyncio
    async def test_delete_contact_success(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        session,
        test_organization,
        test_user,
    ):
        """Can delete a contact without deals."""
        # Create a contact specifically for deletion
        from app.models import Contact

        contact = Contact(
            organization_id=test_organization.id,
            owner_id=test_user.id,
            name="To Delete",
        )
        session.add(contact)
        await session.commit()
        await session.refresh(contact)

        response = await client.delete(
            f"/api/v1/contacts/{contact.id}",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_contact_with_deals_fails(
        self,
        client: AsyncClient,
        auth_headers_with_org: dict,
        test_contact: Contact,
        test_deal,
    ):
        """Cannot delete contact with active deals."""
        response = await client.delete(
            f"/api/v1/contacts/{test_contact.id}",
            headers=auth_headers_with_org,
        )

        assert response.status_code == 409
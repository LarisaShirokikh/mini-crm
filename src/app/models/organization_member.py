from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import OrganizationRole

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class OrganizationMember(Base):
    """
    Organization membership model.

    Links users to organizations with specific roles.
    A user can be a member of multiple organizations.
    """

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_member",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[OrganizationRole] = mapped_column(
        String(50),
        nullable=False,
        default=OrganizationRole.MEMBER,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="memberships",
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationMember(org_id={self.organization_id}, "
            f"user_id={self.user_id}, role='{self.role}')>"
        )

    # Permission helpers
    def can_manage_organization(self) -> bool:
        """Check if member can manage organization settings."""
        return OrganizationRole.can_manage_organization(self.role)

    def can_manage_all_entities(self) -> bool:
        """Check if member can manage all entities."""
        return OrganizationRole.can_manage_all_entities(self.role)

    def can_rollback_stage(self) -> bool:
        """Check if member can rollback deal stage."""
        return OrganizationRole.can_rollback_stage(self.role)
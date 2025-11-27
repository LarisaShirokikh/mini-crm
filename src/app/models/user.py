from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.contact import Contact
    from app.models.deal import Deal
    from app.models.organization_member import OrganizationMember


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    memberships: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    owned_contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="owner",
        foreign_keys="Contact.owner_id",
    )
    owned_deals: Mapped[list["Deal"]] = relationship(
        "Deal",
        back_populates="owner",
        foreign_keys="Deal.owner_id",
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="author",
        foreign_keys="Activity.author_id",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
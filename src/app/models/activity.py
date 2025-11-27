from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ActivityType

if TYPE_CHECKING:
    from app.models.deal import Deal
    from app.models.user import User


class Activity(Base):
    """
    Activity model.

    Represents timeline entries for a deal: comments, status changes, etc.
    """

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # Null for system events
        index=True,
    )
    type: Mapped[ActivityType] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    deal: Mapped["Deal"] = relationship(
        "Deal",
        back_populates="activities",
    )
    author: Mapped["User | None"] = relationship(
        "User",
        back_populates="activities",
        foreign_keys=[author_id],
    )

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, type='{self.type}', deal_id={self.deal_id})>"
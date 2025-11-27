from enum import Enum


class OrganizationRole(str, Enum):
    """User roles within an organization."""

    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

    @classmethod
    def can_manage_organization(cls, role: "OrganizationRole") -> bool:
        """Check if role can manage organization settings."""
        return role in (cls.OWNER, cls.ADMIN)

    @classmethod
    def can_manage_all_entities(cls, role: "OrganizationRole") -> bool:
        """Check if role can manage all entities (not just own)."""
        return role in (cls.OWNER, cls.ADMIN, cls.MANAGER)

    @classmethod
    def can_rollback_stage(cls, role: "OrganizationRole") -> bool:
        """Check if role can rollback deal stage."""
        return role in (cls.OWNER, cls.ADMIN)


class DealStatus(str, Enum):
    """Deal statuses."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"

    def is_closed(self) -> bool:
        """Check if status is terminal."""
        return self in (DealStatus.WON, DealStatus.LOST)


class DealStage(str, Enum):
    """Deal pipeline stages (ordered)."""

    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED = "closed"

    @classmethod
    def get_order(cls, stage: "DealStage") -> int:
        """Get numeric order of stage for comparison."""
        order = {
            cls.QUALIFICATION: 1,
            cls.PROPOSAL: 2,
            cls.NEGOTIATION: 3,
            cls.CLOSED: 4,
        }
        return order[stage]

    @classmethod
    def is_forward_transition(cls, from_stage: "DealStage", to_stage: "DealStage") -> bool:
        """Check if transition is forward (allowed for all roles)."""
        return cls.get_order(to_stage) > cls.get_order(from_stage)

    @classmethod
    def is_backward_transition(cls, from_stage: "DealStage", to_stage: "DealStage") -> bool:
        """Check if transition is backward (only admin/owner)."""
        return cls.get_order(to_stage) < cls.get_order(from_stage)


class ActivityType(str, Enum):
    """Types of activities in deal timeline."""

    COMMENT = "comment"
    STATUS_CHANGED = "status_changed"
    STAGE_CHANGED = "stage_changed"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    SYSTEM = "system"
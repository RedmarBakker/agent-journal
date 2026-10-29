from dataclasses import dataclass
from datetime import datetime

from journal.features.organization.support.approval_action import ApprovalAction
from journal.models.model import Model


@dataclass(frozen=True)
class Approval(Model):
    """A user's time-limited decision on one action by an agent acting as a Role on a task."""

    PENDING = "pending"
    APPROVED = "approved"
    REFUSED = "refused"
    EXPIRED = "expired"

    environment_id: int = 0
    actor: str = ""
    role: str = ""
    plan_id: int = 0
    task_id: int = 0
    action: ApprovalAction = ApprovalAction.PRODUCTION_DEPLOYMENT
    request_hash: str = ""
    request_details: str = ""
    question_id: int = 0
    question_environment_id: int = 0
    expires_at: datetime | None = None
    decision: str = PENDING
    decided_at: datetime | None = None
    used_at: datetime | None = None

    def decided(self, decision: str, time: datetime) -> "Approval":
        return self.with_(decision=decision, decided_at=time)

    def used(self, time: datetime) -> "Approval":
        return self.with_(used_at=time)

    def permits(self, time: datetime) -> bool:
        return self.decision == self.APPROVED and self.used_at is None and self.expires_at is not None and self.expires_at > time

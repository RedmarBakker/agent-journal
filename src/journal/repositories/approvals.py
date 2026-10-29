from journal.models.approval import Approval
from journal.repositories.repository import Repository


class Approvals(Repository[Approval]):
    model = Approval

    def for_action(self, actor: str, role: str, plan_id: int, task_id: int, action: str, request_hash: str) -> Approval | None:
        rows = self.matching(actor=actor, role=role, plan_id=plan_id, task_id=task_id, action=action, request_hash=request_hash)
        return rows[-1] if rows else None

from journal.models.approval import Approval
from journal.repositories.repository import Repository


class Approvals(Repository[Approval]):
    model = Approval

    def for_action(self, actor: str, role: str, task_id: int, action: str) -> Approval | None:
        rows = self.matching(actor=actor, role=role, task_id=task_id, action=action)
        return rows[0] if rows else None

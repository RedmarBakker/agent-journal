from dataclasses import dataclass

from journal.models.board_phase import BoardPhase
from journal.models.plan import Plan
from journal.models.task import Task


@dataclass(frozen=True)
class DomainPlan:
    """A plan as one domain sees it: the plan, only its tasks handed to that domain's Roles, and which of the domain's tasks wait on a proof check, a check or an approval."""

    plan: Plan
    tasks: tuple[Task, ...]
    reviewed: frozenset[int]

    def is_active(self) -> bool:
        return any(task.is_handed_out() for task in self.tasks)

    def is_on_board(self) -> bool:
        return bool(self.tasks)

    def phase(self) -> BoardPhase:
        return BoardPhase.of(self.tasks, self.reviewed)

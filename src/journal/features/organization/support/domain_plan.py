from dataclasses import dataclass

from journal.models.board_phase import BoardPhase
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.task import Task
from journal.models.task_state import TaskState


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

    def waits_on(self) -> str:
        if self.plan.state == PlanState.READY:
            return "your approval"
        if self.plan.state == PlanState.REVIEWING:
            return "plan review"
        if self.plan.is_blocked():
            return self.plan.waiting_reason() or "the plan to be unblocked"
        reason = next((task.waiting_reason() for task in self.tasks if task.waiting_reason()), "")
        if reason:
            return reason
        if self.phase() == BoardPhase.IN_REVIEW:
            return "a proof check or approval"
        if self.is_active():
            return "Role work"
        if self.phase() != BoardPhase.DONE:
            return "a Role to start the next task"
        return ""

    def done_count(self) -> int:
        return sum(1 for task in self.tasks if task.state == TaskState.COMPLETED)

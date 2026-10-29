from dataclasses import dataclass

from journal.models.plan import Plan
from journal.models.task import Task


@dataclass(frozen=True)
class DomainPlan:
    """A plan as one domain sees it: the plan and only its tasks handed to that domain's Roles."""

    plan: Plan
    tasks: tuple[Task, ...]

    def is_active(self) -> bool:
        return any(task.is_handed_out() for task in self.tasks)

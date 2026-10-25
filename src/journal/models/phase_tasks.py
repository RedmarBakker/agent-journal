from collections import Counter
from dataclasses import dataclass

from journal.models.phase import Phase
from journal.models.phase_states import PhaseStates
from journal.models.task import Task


@dataclass(frozen=True)
class PhaseTasks:
    """A phase of a plan with its number from 1 and its tasks in order, as the repository hands them to the plan."""

    number: int
    phase: Phase
    tasks: tuple[Task, ...]

    def states(self) -> PhaseStates:
        return PhaseStates(self.number, self.phase, tuple(task.id for task in self.tasks), dict(Counter(task.state for task in self.tasks)))

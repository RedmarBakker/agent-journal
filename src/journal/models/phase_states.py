from dataclasses import dataclass

from journal.models.phase import Phase
from journal.models.task_state import TaskState


@dataclass(frozen=True)
class PhaseStates:
    """A phase of a plan with its number from 1 and how many of its tasks are in each state, which is all the plan asks of a phase to find the one in hand and a checkpoint."""

    number: int
    phase: Phase
    state_counts: dict[TaskState, int]

    def has_tasks(self) -> bool:
        return any(self.state_counts.values())

    def is_finished(self) -> bool:
        return self.has_tasks() and not self.has_open_work()

    def has_open_work(self) -> bool:
        return any(count for state, count in self.state_counts.items() if not state.is_closed())

    def has_work_completed(self) -> bool:
        return bool(self.state_counts.get(TaskState.COMPLETED, 0))

    def has_work_started(self) -> bool:
        return any(self.state_counts.get(state, 0) for state in (TaskState.STARTED, TaskState.COMPLETED))

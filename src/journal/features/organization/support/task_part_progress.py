from dataclasses import dataclass

from journal.models.task_state import TaskState


@dataclass(frozen=True)
class TaskPartProgress:
    """A plan task's ordered Role parts and their current work states."""

    parent_id: int
    part_ids: tuple[int, ...]
    roles: tuple[str, ...]
    states: tuple[TaskState, ...]
    delegated: tuple[bool, ...]
    waiting_on: tuple[tuple[int, ...], ...]

    def ready_parts(self) -> tuple[tuple[int, str], ...]:
        return tuple(
            (part_id, role)
            for part_id, role, state, delegated, waits in zip(
                self.part_ids, self.roles, self.states, self.delegated, self.waiting_on,
            )
            if state == TaskState.OPEN and not delegated and not waits and role.startswith("role:")
        )

    def all_completed(self) -> bool:
        return all(state == TaskState.COMPLETED for state in self.states)

    def all_cancelled(self) -> bool:
        return all(state == TaskState.CANCELLED for state in self.states)

    def completed_count(self) -> int:
        return sum(state == TaskState.COMPLETED for state in self.states)

from dataclasses import dataclass


@dataclass(frozen=True)
class Assignment:
    """The task an agent was handed next and why, or none, with the tasks after it when more than one was asked for, in the order the assigner would hand them."""

    task_id: int = 0
    title: str = ""
    reason: str = ""
    following_ids: tuple[int, ...] = ()

    def has_task(self) -> bool:
        return self.task_id > 0

    def task_ids(self) -> tuple[int, ...]:
        return (self.task_id, *self.following_ids) if self.has_task() else ()

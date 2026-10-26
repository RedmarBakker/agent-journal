from dataclasses import dataclass


@dataclass(frozen=True)
class Assignment:
    """The task an agent was handed next and why, or none."""

    task_id: int = 0
    title: str = ""
    reason: str = ""

    def has_task(self) -> bool:
        return self.task_id > 0

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskBlock:
    """The task an environment's running agent has, and what it waits for on it while a pause is on top."""

    id: int
    title: str
    wait_text: str

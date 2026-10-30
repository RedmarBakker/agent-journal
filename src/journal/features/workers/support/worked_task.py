from dataclasses import dataclass

from journal.models.task import Task


@dataclass(frozen=True)
class WorkedTask:
    """A task a worker held at some time as its page lists it: the number, the title and the state, done once the worker finished it and its work waits for the merge, whatever state the task row still holds, merged after, in hand while the worker works on it, else the task's own state."""

    id: int
    title: str
    state: str

    @classmethod
    def read(cls, task: Task, unmerged: list[int]) -> "WorkedTask":
        return cls(task.id, task.title, cls.state_word(task, unmerged))

    @staticmethod
    def state_word(task: Task, unmerged: list[int]) -> str:
        if task.id in unmerged:
            return "done"
        if task.is_completed():
            return "merged"
        return "in hand" if task.is_open() and task.delegated else task.state.value

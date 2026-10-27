from dataclasses import dataclass

from journal.models.task import Task


@dataclass(frozen=True)
class WorkedTask:
    """A task a worker held at some time as its page lists it: the number, the title and the state, in hand while the worker works on it, done once the worker finished it and its work is not merged yet, merged after, else the task's own state."""

    id: int
    title: str
    state: str

    @classmethod
    def read(cls, task: Task, unmerged: list[int]) -> "WorkedTask":
        return cls(task.id, task.title, cls.state_word(task, unmerged))

    @staticmethod
    def state_word(task: Task, unmerged: list[int]) -> str:
        if task.is_open() and task.delegated:
            return "in hand"
        if not task.is_completed():
            return task.state.value
        return "done" if task.id in unmerged else "merged"

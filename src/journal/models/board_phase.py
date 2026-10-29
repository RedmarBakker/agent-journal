from collections.abc import Iterable
from enum import StrEnum

from journal.models.task import Task


class BoardPhase(StrEnum):
    """The four base phases of a domain's board, each with one fixed meaning to journal, and the one function that says which a plan stands in from the domain's tasks in it."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"

    @classmethod
    def of(cls, tasks: Iterable[Task], reviewed: frozenset[int]) -> "BoardPhase":
        open_tasks = [task for task in tasks if not task.is_closed()]
        if not open_tasks:
            return cls.DONE
        if any(task.id in reviewed for task in open_tasks):
            return cls.IN_REVIEW
        if any(task.is_started() for task in open_tasks):
            return cls.IN_PROGRESS
        return cls.PLANNED

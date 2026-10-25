from typing import ClassVar

from journal.db.migration import Migration


class PrioritySet(Migration):
    """A task made before the agent was asked to give each its priority has its priority as it stands: set, so no old task is asked about."""

    number: ClassVar[int] = 58
    statements: ClassVar[tuple[str, ...]] = ("UPDATE tasks SET priority_set = 1",)

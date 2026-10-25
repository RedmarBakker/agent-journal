from typing import ClassVar

from journal.db.migration import Migration


class DelegatedFlag(Migration):
    """Delegated stops being a task state and becomes a flag on the task: every delegated task keeps the state it really has, started when a worker holds it in hand, open when it waits in a queue or is completed and not yet merged, and every other task is not delegated."""

    number: ClassVar[int] = 57
    statements: ClassVar[tuple[str, ...]] = (
        "UPDATE tasks SET delegated = 0 WHERE delegated IS NULL",
        "UPDATE tasks SET delegated = 1, state = CASE WHEN 'tasks:' || id IN (SELECT target FROM links WHERE kind = 'in_hand' AND source LIKE 'workers:%') THEN 'started' ELSE 'open' END WHERE state = 'delegated'",
    )

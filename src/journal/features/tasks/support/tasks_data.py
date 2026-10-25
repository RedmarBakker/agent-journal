from dataclasses import dataclass

from journal.models.open_task import OpenTask


@dataclass(frozen=True)
class TasksData:
    """The tasks feature's reading for an agent: its own task in hand, the paused, the blocked, the tasks whose wait is broken, the first open tasks and how many are open, and the tasks it took in hand most recently."""

    current_task: int
    last_log_line: str
    paused: tuple[int, ...]
    pause_summary: str
    blocked: tuple[int, ...]
    blocked_without_wait: tuple[int, ...]
    blocked_without_wait_summary: str
    broken_waits: tuple[int, ...]
    broken_waits_summary: str
    first_pause_reason: str
    next_open: OpenTask | None
    last_commands: tuple[str, ...]
    open_ids: tuple[int, ...] = ()
    open_next: str = ""
    open_count: int = 0
    started_ids: tuple[int, ...] = ()
    agent_tasks: tuple[int, ...] = ()

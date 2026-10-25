from collections.abc import Mapping
from dataclasses import dataclass, field

from journal.features.tasks.support.wait_progress import WaitProgress
from journal.models.open_task import OpenTask


@dataclass(frozen=True)
class TasksData:
    """The tasks feature's reading for an agent: its own task in hand, the paused, the blocked, the tasks whose wait is broken, the first open tasks and how many are open, the tasks it took in hand most recently, what a task of each hub environment is called, acme task for the hub of acme, when each blocked or paused task that waits on no person last changed, the blocked or paused tasks that wait on a person, how far each of the agent's own runs still going has come, and the open tasks the agent made that sit at the default priority, those that hold its writes once they are enough."""

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
    task_nouns: Mapping[int, str] = field(default_factory=dict)
    last_moves: Mapping[int, float] = field(default_factory=dict)
    person_waits: tuple[int, ...] = ()
    wait_progress: Mapping[str, WaitProgress] = field(default_factory=dict)
    unprioritised: tuple[int, ...] = ()
    blocking_priorities: tuple[int, ...] = ()

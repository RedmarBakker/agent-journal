from collections.abc import Mapping
from dataclasses import dataclass, field

from journal.features.tasks.support.passed_wait import PassedWait
from journal.features.tasks.support.wait_progress import WaitProgress
from journal.models.open_task import OpenTask
from journal.models.task import Task


@dataclass(frozen=True)
class TasksData:
    """The tasks feature's reading for an agent: its own task in hand, the blocked, those blocked with no wait and how many tasks were completed since they were last named and from when, the tasks whose wait is broken, the first open tasks and how many are open, the tasks it took in hand most recently, what a task of each hub environment is called, acme task for the hub of acme, when each blocked task that waits on no person last changed, the blocked tasks that wait on a person, how far each of the agent's own runs still going has come, the open tasks the agent made that sit at the default priority, those that hold its writes once they are enough, and its open work: the next open task, in auto mode or not, never the task in hand; and the task in hand itself, for how long it has been in progress."""

    current_task: int
    last_log_line: str
    blocked: tuple[int, ...]
    blocked_without_wait: tuple[int, ...]
    blocked_without_wait_summary: str
    broken_waits: tuple[int, ...]
    broken_waits_summary: str
    next_open: OpenTask | None
    last_commands: tuple[str, ...]
    open_ids: tuple[int, ...] = ()
    open_next: str = ""
    open_count: int = 0
    started_ids: tuple[int, ...] = ()
    agent_tasks: tuple[int, ...] = ()
    last_moves: Mapping[int, float] = field(default_factory=dict)
    person_waits: tuple[int, ...] = ()
    wait_progress: Mapping[str, WaitProgress] = field(default_factory=dict)
    unprioritised: tuple[int, ...] = ()
    blocking_priorities: tuple[int, ...] = ()
    polled_checks: tuple[int, ...] = ()
    passed_waits: tuple[PassedWait, ...] = ()
    loose_blocks_since: float = 0.0
    completed_since_loose_blocks: int = 0
    command_lines: tuple[str, ...] = ()
    turn_finished: bool = False
    wake_count: int = 0
    open_work: OpenTask | None = None
    current_task_row: Task | None = None

from collections.abc import Mapping
from dataclasses import dataclass, field

from journal.features.tasks.support.passed_wait import PassedWait
from journal.features.tasks.support.wait_progress import WaitProgress
from journal.models.open_task import OpenTask


@dataclass(frozen=True)
class TasksData:
    """The tasks feature's reading for an agent: its own task in hand, the paused, the blocked, the tasks whose wait is broken, the first open tasks and how many are open, the tasks it took in hand most recently, what a task of each hub environment is called, acme task for the hub of acme, when each blocked or paused task that waits on no person last changed, the blocked or paused tasks that wait on a person, how far each of the agent's own runs still going has come, the open tasks the agent made that sit at the default priority, those that hold its writes once they are enough, the paused work it may choose to take up, whether a free open task waits beside it, whether the agent set its paused work aside until its next close, and its open work: its own paused task or the next open task, in auto mode or not, never the task in hand."""

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
    polled_checks: tuple[int, ...] = ()
    passed_waits: tuple[PassedWait, ...] = ()
    choosable: tuple[int, ...] = ()
    choosable_summary: str = ""
    free_open: bool = False
    paused_declined: bool = False
    command_lines: tuple[str, ...] = ()
    turn_finished: bool = False
    wake_count: int = 0
    open_work: OpenTask | None = None

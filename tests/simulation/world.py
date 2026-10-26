from dataclasses import dataclass, field


@dataclass
class World:
    """What the simulated actors know of the journal between steps: the open tasks by number, the workers out with the moment each finishes, the workers whose work waits to merge, the workers merged and idle, the user's messages not yet answered, and the next numbers to give."""

    open_tasks: list[int] = field(default_factory=list)
    workers_out: dict[int, float] = field(default_factory=dict)
    workers_done: list[int] = field(default_factory=list)
    idle_workers: list[int] = field(default_factory=list)
    unread_messages: int = 0
    next_task: int = 1
    next_worker: int = 1

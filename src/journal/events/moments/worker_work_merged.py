from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class WorkerWorkMerged(Event):
    """A worker's work was merged and its task closed, and the worker was sent on to the next task of its queue, next_task, or is idle when that is 0; with the lines it brought in and the shas of the worker's commits taken in."""

    environment_id: int
    worker: int
    name: str
    dispatcher: str | None
    task: int
    next_task: int
    time: float
    lines: int = 0
    merged_shas: tuple[str, ...] = ()

from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class WorkerMergeRefused(Event):
    """A worker's merge was refused on a clash with the branch it merges into: clashing names where, and line says it with the command that sends the worker back."""

    environment_id: int
    worker: int
    name: str
    dispatcher: str | None
    task: int
    clashing: str
    line: str

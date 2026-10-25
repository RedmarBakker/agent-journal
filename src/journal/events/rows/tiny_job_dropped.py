from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class TinyJobDropped(RowEvent):
    """A worker reported within a minute of its job's start with no other task open, a job so small its dispatcher should have done it itself, which cost the dispatcher a larger drop at once: the dispatcher's session, the worker, the seconds the job took and the points it cost."""

    agent_session: str
    worker: int
    seconds: int
    points: int

from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class QuickReportDropped(RowEvent):
    """A worker reported within minutes of its job's start while plenty of work was open, which cost its dispatcher a drop in its fitness at once: the dispatcher's session, the worker, the tasks open then and the points it cost."""

    feature_name = "workers"

    agent_session: str
    worker: int
    open_tasks: int
    points: int

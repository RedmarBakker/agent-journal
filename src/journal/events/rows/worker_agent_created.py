from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerAgentCreated(RowEvent):
    """A worker's session got its agent row, so a worker that clocked in before it can be put to work."""

    feature_name = "workers"

    agent_session: str = ""

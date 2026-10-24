from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class JobStopRequested(RowEvent):
    """The user requested from the viewer to stop a job an agent scheduled for itself, by the agent's session and the job's id."""

    agent_session: str
    job_id: str

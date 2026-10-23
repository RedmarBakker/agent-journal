from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class JobCancel(Operation):
    """The agent ending a job it scheduled with its program's own tool, by the job's id."""

    kind = "job cancel"
    job_id: str

from datetime import datetime, timezone

from journal.models.edit import Edit
from journal.models.worker import Worker
from journal.repositories.edits import Edits


class MergedWork:
    """The edits a worker made during a selected part of its job."""

    def __init__(self, edits: Edits) -> None:
        self.edits = edits

    def job_edits_between(self, worker: Worker, start: float, end: float) -> list[Edit]:
        session = worker.conversation()
        return self.edits.selected(self.edits.query().filter(session=session).filter_greater_equal("time", start).filter_less_equal("time", end).order("id")) if session else []

    @staticmethod
    def moment(time: float) -> datetime:
        return datetime.fromtimestamp(time, timezone.utc)

    @staticmethod
    def is_test(path: str) -> bool:
        return bool(TEST_FILE.search(PurePosixPath(path).as_posix()))

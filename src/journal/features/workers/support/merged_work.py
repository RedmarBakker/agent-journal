import re
from datetime import datetime, timezone
from pathlib import PurePosixPath

from journal.features.workers.support.tool_use_counts import NAMED_FILES
from journal.features.workers.support.work_complexity import WorkComplexity
from journal.models.edit import Edit
from journal.models.worker import Worker
from journal.repositories.edits import Edits
from journal.repositories.entries import Entries
from journal.support.actor import Actor

# the moves that start a worker's job, the send-back that hands it back, and the merge that ends it
STARTS = ("dispatched", "sent a job")
SENT_BACK, MERGED = "sent back", "merged"
TEST_FILE = re.compile(r"(^|/)tests?/|(^|/)test_[^/]+$|[^/]+_test\.\w+$|\.test\.\w+$|\.spec\.\w+$")


class MergedWork:
    """A worker's job that was just merged, as its records tell it: the span from the move that started the job to its merge, the send-backs in it, the edits its session made in it, with the lines and files they changed and the test files among them, its tool uses counted from its entries, and whether its brief named the files to change."""

    def __init__(self, edits: Edits, entries: Entries) -> None:
        self.edits, self.entries = edits, entries

    def complexity(self, worker: Worker) -> WorkComplexity:
        start, end, send_backs = self.span(worker)
        session = worker.conversation()
        edits = self.job_edits(worker)
        paths = {edit.path for edit in edits}
        tool_uses = self.entries.counted(self.entries.query().filter(actor=Actor.agent(session), kind="ToolStarting").filter_greater_equal("created_at", self.moment(start)).filter_less_equal("created_at", self.moment(end))) if session else 0
        return WorkComplexity(lines=sum(edit.added + edit.removed for edit in edits), files=len(paths), send_backs=send_backs, tool_uses=tool_uses,
                              minutes=round((end - start) / 60, 1), tests_added=sum(1 for path in paths if self.is_test(path)), brief_named_files=bool(NAMED_FILES.search(worker.brief)))

    def job_edits(self, worker: Worker) -> list[Edit]:
        start, end, _ = self.span(worker)
        session = worker.conversation()
        return self.edits.selected(self.edits.query().filter(session=session).filter_greater_equal("time", start).filter_less_equal("time", end).order("id")) if session else []

    @staticmethod
    def span(worker: Worker) -> tuple[float, float, int]:
        steps = worker.moves.steps
        end = next((time for word, time in reversed(steps) if word == MERGED), steps[-1][1] if steps else 0.0)
        start = next((time for word, time in reversed(steps) if word in STARTS and time <= end), steps[0][1] if steps else end)
        return start, end, sum(1 for word, time in steps if word == SENT_BACK and start <= time <= end)

    @staticmethod
    def moment(time: float) -> datetime:
        return datetime.fromtimestamp(time, timezone.utc)

    @staticmethod
    def is_test(path: str) -> bool:
        return bool(TEST_FILE.search(PurePosixPath(path).as_posix()))

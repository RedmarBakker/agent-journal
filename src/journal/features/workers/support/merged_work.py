import re
from datetime import datetime, timezone
from pathlib import PurePosixPath

from journal.features.workers.support.job_span import JobSpan
from journal.features.workers.support.work_complexity import WorkComplexity
from journal.models.edit import Edit
from journal.models.worker import JOB_STARTS, MERGED, REJECTION_MOVE, Worker
from journal.repositories.edits import Edits
from journal.repositories.entries import Entries
from journal.support.actor import Actor

# a path or a file name a brief or a change names
FILE_PATTERN = re.compile(r"[\w-]+/[\w./-]+|\b[\w-]+\.(?:py|js|ts|vue|md|json|sh|php|go|css|html)\b|--changes")

TEST_FILE = re.compile(r"(^|/)tests?/|(^|/)test_[^/]+$|[^/]+_test\.\w+$|\.test\.\w+$|\.spec\.\w+$")


class MergedWork:
    """A worker's job that was just merged, as its records tell it: the span from the move that started the job to its merge, the send-backs in it, the edits its session made in it, with the lines and files they changed and the test files among them, its tool uses counted from its entries, and whether its brief named the files to change."""

    def __init__(self, edits: Edits, entries: Entries) -> None:
        self.edits, self.entries = edits, entries

    def complexity(self, worker: Worker) -> WorkComplexity:
        span = self.span(worker)
        session = worker.conversation()
        edits = self.job_edits(worker)
        paths = {edit.path for edit in edits}
        tool_uses = self.entries.counted(self.entries.query().filter(actor=Actor.agent(session), entry_type="ToolStarting").filter_greater_equal("created_at", self.moment(span.start)).filter_less_equal("created_at", self.moment(span.end))) if session else 0
        return WorkComplexity(lines=sum(edit.added + edit.removed for edit in edits), files=len(paths), send_backs=span.rejection_count, tool_uses=tool_uses,
                              minutes=round((span.end - span.start) / 60, 1), tests_added=sum(1 for path in paths if self.is_test(path)), brief_named_files=bool(FILE_PATTERN.search(worker.brief)))

    def job_edits(self, worker: Worker) -> list[Edit]:
        span = self.span(worker)
        session = worker.conversation()
        return self.edits.selected(self.edits.query().filter(session=session).filter_greater_equal("time", span.start).filter_less_equal("time", span.end).order("id")) if session else []

    @staticmethod
    def span(worker: Worker) -> JobSpan:
        steps = worker.moves.steps
        end = next((time for word, time in reversed(steps) if word == MERGED), steps[-1][1] if steps else 0.0)
        start = next((time for word, time in reversed(steps) if word in JOB_STARTS and time <= end), steps[0][1] if steps else end)
        return JobSpan(start, end, sum(1 for word, time in steps if word == REJECTION_MOVE and start <= time <= end))

    @staticmethod
    def moment(time: float) -> datetime:
        return datetime.fromtimestamp(time, timezone.utc)

    @staticmethod
    def is_test(path: str) -> bool:
        return bool(TEST_FILE.search(PurePosixPath(path).as_posix()))

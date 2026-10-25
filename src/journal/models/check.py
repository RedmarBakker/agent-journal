from typing import ClassVar
from dataclasses import dataclass
from datetime import datetime

from journal.support.check_progress import CheckProgress
from journal.support.check_report import CheckReport
from journal.events.rows.check_completed import CheckCompleted
from journal.events.rows.row_resolved import RowResolved
from journal.models.model import Model
from journal.support.rejection import Rejection

RUN_LIMIT_SECONDS = 600


@dataclass(frozen=True)
class Check(Model):
    """A script that passes or fails about the project, run by hand or every so many minutes, and when its failure was last reported to the agent; a run force stopped neither passes nor fails. How its runs went is each machine's own and never travels through the team."""

    text_fields: ClassVar[tuple[str, ...]] = ("title", "brief", "command")
    local_fields: ClassVar[tuple[str, ...]] = ("last_passed", "last_output", "last_run_at", "last_duration", "last_report", "progress", "last_fault", "failure_reported_at", "last_stopped")
    title: str = ""
    brief: str = ""
    command: str = ""
    interval: float = 0
    last_passed: bool | None = None
    last_output: str = ""
    last_run_at: datetime | None = None
    last_duration: float = 0.0
    last_report: CheckReport | None = None
    progress: CheckProgress | None = None
    last_fault: str = ""
    wait_target: bool = False
    is_retired: bool = False
    failure_reported_at: float = 0.0
    last_stopped: bool = False

    def edited(self, title: str, brief: str, command: str, interval_minutes: float) -> "Check":
        return self.with_(title=title, brief=brief, command=command, interval=interval_minutes)

    def started(self, time: float) -> "Check":
        return self.with_(progress=CheckProgress(time))

    def is_running(self, moment: float) -> bool:
        return self.progress is not None and moment - self.progress.time < RUN_LIMIT_SECONDS

    def has_run_start(self, started: float) -> bool:
        return self.progress is not None and self.progress.time == started

    def stopped(self, time: datetime) -> "Check":
        if self.progress is None:
            raise Rejection(f"check {self.id} is not running")
        return self.with_(last_passed=None, last_stopped=True, last_output=self.progress.output, last_run_at=time, last_duration=time.timestamp() - self.progress.time, last_report=None, progress=None, last_fault="")

    def verdict(self) -> str:
        if self.last_stopped:
            return "stopped"
        return {True: "passed", False: "failed", None: "not run"}[self.last_passed]

    def completed(self, passed: bool, output: str, time: datetime, elapsed: float, report: CheckReport | None, fault: str) -> "Check":
        executed = CheckCompleted(environment_id=0, time=time.timestamp(), check_id=self.row_id, title=self.title, passed=passed, output=output, prior_failure=self.last_passed is False, wait_target=self.wait_target, failure_reported_at=self.failure_reported_at)
        recorded = self.with_(last_passed=passed, last_stopped=False, last_output=output, last_run_at=time, last_duration=elapsed, last_report=report, progress=None, last_fault=fault).with_event(executed)
        if self.wait_target and passed and not self.is_resolved():
            return recorded.with_event(RowResolved(environment_id=0, time=time.timestamp(), ref=f"{self.table()}:{self.id}", outcome=recorded.outcome()))
        return recorded

    def failure_reported(self, time: float) -> "Check":
        return self.with_(failure_reported_at=time)

    def retired(self, time: float) -> "Check":
        retired = self.with_(is_retired=True, progress=None)
        return retired if self.is_resolved() else retired.with_event(RowResolved(environment_id=0, time=time, ref=f"{self.table()}:{self.id}", outcome=f"check {self.id} removed"))

    def needs_run(self, time: datetime) -> bool:
        if self.is_retired or self.interval <= 0 or (self.wait_target and self.is_resolved()):
            return False
        return self.last_run_at is None or (time - self.last_run_at).total_seconds() >= self.interval * 60

    def is_resolved(self) -> bool:
        return self.last_passed is True or self.is_retired

    def outcome(self) -> str:
        return f"check {self.id} passed"

    def cannot_run(self) -> bool:
        return bool(self.last_fault)

    def title_words(self) -> str:
        return self.title

    def summary_line(self) -> str:
        return self.opening_line(self.brief)

from typing import ClassVar
from dataclasses import dataclass
from journal.models.support.worker_moves import WorkerMoves
from journal.models.support.worker_silence import WorkerSilence
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.worker_reported import WorkerReported
from journal.events.rows.worker_dispatched import WorkerDispatched
from journal.events.rows.worker_stopped import WorkerStopped
from journal.events.rows.worker_ready import WorkerReady
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.events.rows.worker_review_failed import WorkerReviewFailed
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.events.rows.worker_sent_to_review import WorkerSentToReview
from journal.events.rows.worker_merged import WorkerMerged
from journal.events.rows.worker_released import WorkerReleased
from journal.events.rows.worker_unfinished import WorkerUnfinished
from journal.events.rows.worker_notified import WorkerNotified
from journal.events.rows.worker_retired import WorkerRetired
from journal.events.rows.worker_reused import WorkerReused
from journal.events.rows.worker_revived import WorkerRevived
from journal.events.rows.worker_queue_drained import WorkerQueueDrained
from journal.models.helper import Helper
from journal.models.reviewer import Reviewer
from journal.models.support.path_overlap import PathOverlap
from journal.models.worker_state import WorkerState
from journal.support.rejection import Rejection
from journal.support.timeout import Timeout

SILENCE = Timeout.minutes(20)


@dataclass(frozen=True)
class Worker(Helper):
    """An agent sent to write one bounded job, in a worktree of its own when it changes code: out while dispatched whatever its process, so one ended unreported or mid-report still counts as out until its report is filed; idle once it reported, until its report is acted on; in review while the journal's reviewer reviews what it clocked out with; retired once stopped or acted on. It keeps each move it made with its time, the branch it commits on, and, for one sent to the team's pool, the team server's number of the request that asked for it and the branch on origin its worktree is cut from."""

    text_fields: ClassVar[tuple[str, ...]] = ("name", "brief")
    kind: str = "worker"
    profile: str | None = None
    worktree: bool = False
    repositories: tuple[str, ...] = ()
    library_links: tuple[str, ...] = ()
    library_copies: tuple[str, ...] = ()
    state: WorkerState = WorkerState.DISPATCHED
    dispatcher: str | None = None
    resume: str = ""
    adopted: bool = False
    device: str = ""
    began: float = 0.0
    recovered_session: str = ""
    touched_paths: tuple[str, ...] | None = None
    reuse_count: int = 0
    retire_reason: str = ""
    run_end: str = ""
    transcript_bytes: int = 0
    silence: WorkerSilence = WorkerSilence(SILENCE)
    moves: WorkerMoves = WorkerMoves()
    branch: str = ""
    pool_request: int = 0
    base: str = ""
    edited_task: int = 0
    in_review: bool = False

    def conversation(self) -> str:
        return self.resume or self.session or self.recovered_session

    def mention(self) -> WorkerMention:
        return WorkerMention(self.row_id, self.name, self.dispatcher)

    def dispatched(self, time: float) -> "Worker":
        return self.contacted(time).moved("dispatched", time).with_(state=WorkerState.DISPATCHED).with_event(self.pending(WorkerDispatched, time))

    def pending(self, kind: type[WorkerDispatched], time: float) -> WorkerDispatched:
        return kind(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), label=self.mention().label(), awaiter=self.dispatcher, brief=self.brief)

    def reported(self, time: float, report: int) -> "Worker":
        return self.contacted(time).moved("reported", time).with_(state=WorkerState.REPORTED, adopted=False, pid=0).with_event(WorkerReported(environment_id=self.environment_id, time=time, worker=self.mention(), report=report, ref=self.mention().ref(), outcome=f"{self.mention().title()}, reported"))

    def queue_drained(self, task_ids: list[int], time: float) -> "Worker":
        return self.with_event(WorkerQueueDrained(environment_id=self.environment_id, time=time, worker=self.mention(), tasks=f"tasks {', '.join(map(str, task_ids))} are open again"))

    def ready(self, time: float) -> "Worker":
        return self.contacted(time).moved("clocked in", time).with_(state=WorkerState.READY).with_event(WorkerReady(environment_id=self.environment_id, time=time, worker=self.mention()))

    def delivered(self, time: float) -> "Worker":
        return self.contacted(time).moved("clocked out", time).with_(state=WorkerState.DELIVERED).with_event(WorkerDelivered(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, clocked out"))

    def delivered_to_review(self, time: float, report: str) -> "Worker":
        return self.contacted(time).moved("clocked out", time).with_(state=WorkerState.DELIVERED, in_review=True).with_event(WorkerSentToReview(environment_id=self.environment_id, time=time, worker=self.mention(), report=report))

    def reviewed(self, time: float, task: int, reviewer: Reviewer, report: str) -> "Worker":
        return self.review_ended(time, "reviewed").with_event(WorkerReviewed(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, reviewed", task=task, reviewer=reviewer.id, reviewer_session=reviewer.session, report=report))

    def review_failed(self, time: float, task: int, reviewer: Reviewer) -> "Worker":
        return self.review_ended(time, "review ended without a report").with_event(WorkerReviewFailed(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, its review ended without a report", task=task, reviewer=reviewer.id))

    def review_ended(self, time: float, move: str) -> "Worker":
        if not self.in_review:
            raise Rejection(f"worker {self.id} has no work in review")
        return self.contacted(time).moved(move, time).with_(in_review=False)

    def unfinished(self, time: float, text: str) -> "Worker":
        return self.moved("ended without clocking out", time).with_(state=WorkerState.UNFINISHED, pid=0, token_hash="", run_end=text).with_event(WorkerUnfinished(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, ended without clocking out"))

    def merged(self, time: float) -> "Worker":
        return self.moved("merged", time).with_(state=WorkerState.MERGED, token_hash="").with_event(WorkerMerged(environment_id=self.environment_id, time=time, worker=self.mention()))

    def released(self, time: float) -> "Worker":
        return self.moved("released", time).with_(state=WorkerState.RELEASED, token_hash="").with_event(WorkerReleased(environment_id=self.environment_id, time=time, worker=self.mention()))

    def running_as(self, pid: int, began: float) -> "Worker":
        return self.with_(pid=pid, began=began, recovered_session="")

    def resumed(self, brief: str, time: float, kind: type[WorkerReused] | type[WorkerRevived], move: str) -> "Worker":
        instructed = self.instructed(brief, time).moved(move, time).with_(reuse_count=self.reuse_count + 1)
        return instructed.with_event(instructed.pending(kind, time))

    def instructed(self, brief: str, time: float) -> "Worker":
        return self.contacted(time).with_(brief=brief, state=WorkerState.DISPATCHED, adopted=False, pid=0, began=0.0, in_review=False)

    def moved(self, move: str, time: float) -> "Worker":
        return self.with_(moves=self.moves.added(move, time))

    def contacted(self, time: float) -> "Worker":
        return self.with_(silence=self.silence.started(time))

    def is_silent(self, time: float) -> bool:
        return self.is_running() and self.silence.is_elapsed(time)

    def notified(self, text: str, time: float, sender: str) -> "Worker":
        return self.contacted(time).with_event(WorkerNotified(environment_id=self.environment_id, time=time, worker=self.mention(), text=text, sender=sender))

    def stopped(self, time: float, reason: str) -> "Worker":
        return self.moved("stopped", time).with_(state=WorkerState.STOPPED, adopted=True, retire_reason=reason, token_hash="").with_event(WorkerStopped(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, stopped before it reported"))

    def finished(self, time: float, reason: str) -> "Worker":
        retired = self.moved("retired", time).with_(adopted=True, retire_reason=reason).with_event(WorkerRetired(environment_id=self.environment_id, time=time, worker=self.mention()))
        return retired.stopped(time, reason) if self.is_running() else retired

    def is_device(self, device: str) -> bool:
        return self.device == device

    def is_running(self) -> bool:
        return self.state in (WorkerState.DISPATCHED, WorkerState.READY)

    def is_awaited(self) -> bool:
        return self.is_running() or self.in_review

    def is_mid_turn(self) -> bool:
        return bool(self.token_hash) and self.is_running()

    def is_active(self) -> bool:
        return self.is_running() or self.state == WorkerState.DELIVERED

    def is_closed(self) -> bool:
        return self.state in (WorkerState.STOPPED, WorkerState.MERGED, WorkerState.RELEASED, WorkerState.UNFINISHED)

    def is_unanswered(self, time: float, seconds: float) -> bool:
        return self.state == WorkerState.DELIVERED and not self.in_review and time - self.silence.timeout.start > seconds

    def is_idle(self) -> bool:
        return self.state == WorkerState.REPORTED and not self.adopted

    def overlaps(self, paths: set[str]) -> bool:
        return PathOverlap.exists(self.touched_paths or (), paths)

    def files_line(self) -> str:
        if self.touched_paths is None:
            return "no files known"
        return ", ".join(self.touched_paths) or "no files changed"

    def title_words(self) -> str:
        return self.name

    def summary_line(self) -> str:
        return self.opening_line(self.brief)

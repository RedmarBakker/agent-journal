from typing import ClassVar
from dataclasses import dataclass
from journal.models.support.worker_moves import WorkerMoves
from journal.models.support.worker_silence import WorkerSilence
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.worker_reported import WorkerReported
from journal.events.rows.worker_test_failed import WorkerTestFailed
from journal.events.rows.worker_spent import WorkerSpent
from journal.models.model_tier import ModelTier
from journal.events.rows.worker_model_judged import WorkerModelJudged
from journal.events.rows.worker_model_mismatch import WorkerModelMismatch
from journal.models.support.model_fit import ModelFit
from journal.events.rows.worker_dispatched import WorkerDispatched
from journal.events.rows.worker_stopped import WorkerStopped
from journal.events.rows.worker_ready import WorkerReady
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.events.rows.worker_review_failed import WorkerReviewFailed
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.events.rows.worker_review_undecided import WorkerReviewUndecided
from journal.events.rows.worker_queue_empty import WorkerQueueEmpty
from journal.events.rows.worker_review_requested import WorkerReviewRequested
from journal.events.rows.worker_merged import WorkerMerged
from journal.events.rows.worker_released import WorkerReleased
from journal.events.rows.worker_limited import WorkerLimited
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
ENDED_UNFINISHED = "ended without clocking out"
# how a run that went past the time limit says it was stopped
RUN_LIMIT_END = "stopped after"
LIMITED_MOVE = "stopped at the usage limit"
RUN_LIMIT_REASON = "run limit"
# the move that hands a worker a point back, and the one that takes its work in
SENT_BACK, MERGED = "sent back", "merged"


@dataclass(frozen=True)
class Worker(Helper):
    """An agent sent to write one bounded job, in a worktree of its own when it changes code: out while dispatched whatever its process, so one ended unreported or mid-report still counts as out until its report is filed; idle once it reported, until its report is acted on; in review while the journal's reviewer reviews what it clocked out with, and queued for review from its clock-out until a reviewer takes it; retired once stopped or acted on. It keeps each move it made with its time, how many of its test runs in a row have failed, how its merged work fit the model it ran on, what its runs have cost in dollars, when its work was last merged and for which task, when it goes on by itself after stopping at the usage limit, the branch it commits on, and, for one sent to the team's pool, the team server's number of the request that asked for it and the branch on origin its worktree is cut from."""

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
    review_pending: bool = False
    failing_runs: int = 0
    model_fit: ModelFit = ModelFit()
    review_queued_at: float = 0.0
    merged_at: float = 0.0
    merged_task: int = 0
    resumes_at: float = 0.0
    cost_dollars: float = 0.0

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

    def failed_run(self, failed: int, time: float) -> "Worker":
        runs = self.failing_runs + 1
        return self.with_(failing_runs=runs).with_event(WorkerTestFailed(environment_id=self.environment_id, time=time, worker=self.mention(), failed=failed, runs=runs))

    def spent(self, cost: float, tier: ModelTier, profile_tier: ModelTier, time: float) -> "Worker":
        total = self.cost_dollars + cost
        return self.with_(cost_dollars=total).with_event(WorkerSpent(environment_id=self.environment_id, time=time, worker=self.mention(), model=self.model, tier=tier, profile_tier=profile_tier, before_dollars=self.cost_dollars, cost_dollars=total))

    def send_backs(self) -> int:
        return self.moves.counted_since(SENT_BACK, MERGED)

    def model_measured(self, fit: ModelFit, send_backs: int, time: float) -> "Worker":
        measured = self.with_(model_fit=fit)
        if not fit.is_mismatch():
            return measured
        return measured.with_event(WorkerModelMismatch(environment_id=self.environment_id, time=time, worker=self.mention(), fit=fit.measured, model=self.model, points=fit.points, send_backs=send_backs))

    def model_judged(self, verdict: str, reason: str, verifier_session: str, time: float) -> "Worker":
        return self.with_(model_fit=self.model_fit.judged(verdict, reason)).with_event(WorkerModelJudged(environment_id=self.environment_id, time=time, worker=self.mention(), verdict=verdict, reason=reason, verifier_session=verifier_session))

    def passed_run(self) -> "Worker":
        return self.with_(failing_runs=0)

    def queue_drained(self, task_ids: list[int], time: float) -> "Worker":
        return self.with_event(WorkerQueueDrained(environment_id=self.environment_id, time=time, worker=self.mention(), tasks=f"tasks {', '.join(map(str, task_ids))} are open again"))

    def ready(self, time: float) -> "Worker":
        return self.contacted(time).moved("clocked in", time).with_(state=WorkerState.READY).with_event(WorkerReady(environment_id=self.environment_id, time=time, worker=self.mention()))

    def delivered(self, time: float) -> "Worker":
        return self.contacted(time).moved("clocked out", time).with_(state=WorkerState.DELIVERED).with_event(WorkerDelivered(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, clocked out"))

    def review_requested(self, time: float, report: str) -> "Worker":
        return self.contacted(time).moved("clocked out", time).with_(state=WorkerState.DELIVERED, review_pending=True, review_queued_at=time).with_event(WorkerReviewRequested(environment_id=self.environment_id, time=time, worker=self.mention(), report=report))

    def reviewed(self, time: float, task: int, reviewer: Reviewer, report: str) -> "Worker":
        return self.review_ended(time, "reviewed").with_event(WorkerReviewed(environment_id=self.environment_id, time=time, worker=self.mention(), task=task, reviewer=reviewer.id, reviewer_session=reviewer.session, report=report))

    def review_undecided(self, time: float, task: int, reviewer: Reviewer, report: str) -> "Worker":
        return self.reviewed(time, task, reviewer, report).with_event(WorkerReviewUndecided(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, its review left for you to decide", task=task, reviewer=reviewer.id, report=report))

    def queue_emptied(self, time: float) -> "Worker":
        return self.with_event(WorkerQueueEmpty(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, merged, with no work left"))

    def review_failed(self, time: float, task: int) -> "Worker":
        return self.review_ended(time, "review ended without a report").with_event(WorkerReviewFailed(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, its review ended without a report", task=task))

    def review_claimed(self) -> "Worker":
        return self.with_(review_queued_at=0.0)

    def review_ended(self, time: float, move: str) -> "Worker":
        if not self.review_pending:
            raise Rejection(f"worker {self.id} has no work in review")
        return self.contacted(time).moved(move, time).with_(review_pending=False, review_queued_at=0.0)

    def unfinished(self, time: float, text: str) -> "Worker":
        times = sum(1 for word, _ in self.moves.steps if word == ENDED_UNFINISHED) + 1
        return self.moved(ENDED_UNFINISHED, time).with_(state=WorkerState.UNFINISHED, pid=0, token_hash="", run_end=text).with_event(WorkerUnfinished(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, ended without clocking out", times=times, is_run_limit=text.startswith(RUN_LIMIT_END)))

    def limited(self, time: float, resumes_at: float, text: str) -> "Worker":
        return self.moved(LIMITED_MOVE, time).with_(state=WorkerState.LIMITED, pid=0, token_hash="", run_end=text, resumes_at=resumes_at).with_event(WorkerLimited(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, waiting for the usage limit", resumes_at=resumes_at))

    def merged(self, task: int, time: float) -> "Worker":
        return self.moved(MERGED, time).with_(state=WorkerState.MERGED, token_hash="", merged_at=time, merged_task=task).with_event(WorkerMerged(environment_id=self.environment_id, time=time, worker=self.mention()))

    def released(self, time: float) -> "Worker":
        return self.moved("released", time).with_(state=WorkerState.RELEASED, token_hash="").with_event(WorkerReleased(environment_id=self.environment_id, time=time, worker=self.mention()))

    def running_as(self, pid: int, began: float) -> "Worker":
        return self.with_(pid=pid, began=began, recovered_session="")

    def resumed(self, brief: str, time: float, kind: type[WorkerReused] | type[WorkerRevived], move: str) -> "Worker":
        instructed = self.instructed(brief, time).moved(move, time).with_(reuse_count=self.reuse_count + 1)
        return instructed.with_event(instructed.pending(kind, time))

    def instructed(self, brief: str, time: float) -> "Worker":
        return self.contacted(time).with_(brief=brief, state=WorkerState.DISPATCHED, adopted=False, pid=0, began=0.0, review_pending=False, review_queued_at=0.0)

    def moved(self, move: str, time: float) -> "Worker":
        return self.with_(moves=self.moves.added(move, time))

    def contacted(self, time: float) -> "Worker":
        return self.with_(silence=self.silence.started(time))

    def is_silent(self, time: float) -> bool:
        return self.is_running() and (self.silence.is_elapsed(time) or self.silence.is_split_due(time))

    def notified(self, text: str, time: float, sender: str) -> "Worker":
        return self.contacted(time).with_event(WorkerNotified(environment_id=self.environment_id, time=time, worker=self.mention(), text=text, sender=sender))

    def stopped(self, time: float, reason: str) -> "Worker":
        return self.moved("stopped", time).with_(state=WorkerState.STOPPED, adopted=True, retire_reason=reason, token_hash="").with_event(WorkerStopped(environment_id=self.environment_id, time=time, worker=self.mention(), ref=self.mention().ref(), outcome=f"{self.mention().title()}, stopped before it reported", is_run_limit=reason == RUN_LIMIT_REASON))

    def finished(self, time: float, reason: str) -> "Worker":
        retired = self.moved("retired", time).with_(adopted=True, retire_reason=reason).with_event(WorkerRetired(environment_id=self.environment_id, time=time, worker=self.mention()))
        return retired.stopped(time, reason) if self.is_running() else retired

    def is_device(self, device: str) -> bool:
        return self.device == device

    def is_running(self) -> bool:
        return self.state in (WorkerState.DISPATCHED, WorkerState.READY)

    def is_pending(self) -> bool:
        return self.is_running() or self.review_pending

    def is_mid_turn(self) -> bool:
        return bool(self.token_hash) and self.is_running()

    def is_active(self) -> bool:
        return self.is_running() or self.state == WorkerState.DELIVERED

    def is_closed(self) -> bool:
        return self.state in (WorkerState.STOPPED, WorkerState.MERGED, WorkerState.RELEASED, WorkerState.UNFINISHED)

    def is_unanswered(self, time: float, seconds: float) -> bool:
        return self.state == WorkerState.DELIVERED and not self.review_pending and time - self.silence.timeout.start > seconds

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

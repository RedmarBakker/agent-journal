import time

from journal.features.reviewing.support.review_brief import ReviewBrief
from journal.features.reviewing.support.review_steps import ReviewSteps
from journal.features.reviewing.support.reviewer_dispatch import ReviewerDispatch
from journal.features.workers.support.worker_reports import WorkerReports
from journal.models.reviewer import Reviewer
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.reviewers import Reviewers
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class ReviewQueue:
    """The reviews waiting for a reviewer, in the order their workers clocked out, handed out by the journal and never the agent: each idle reviewer takes the next, and a queue with no reviewer at all gets its first; a reviewer that cannot be sent hands its worker's work back to the agent at once."""

    def __init__(self, workers: Workers, reviewers: Reviewers, tasks: Tasks, reports: WorkerReports, brief: ReviewBrief, dispatch: ReviewerDispatch, steps: ReviewSteps, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.workers, self.reviewers, self.tasks, self.reports = workers, reviewers, tasks, reports
        self.brief, self.dispatch, self.steps = brief, dispatch, steps

    def assigned(self, environment_id: int) -> None:
        for worker, reviewer in zip(self.workers.queued_reviews(), self.free_reviewers(environment_id)):
            self.assign_review(worker, reviewer)

    def free_reviewers(self, environment_id: int) -> list[Reviewer]:
        if self.reviewers.active() or not self.workers.queued_reviews():
            return self.reviewers.idle()
        return [self.dispatch.added(environment_id)]

    def assign_review(self, worker: Worker, reviewer: Reviewer) -> None:
        task = self.tasks.find(self.tasks.holder_task_ids(Ref.build(worker))[0])
        claimed = self.workers.save(worker.review_claimed(), Actor.system())
        try:
            reviewing = self.dispatch.sent(reviewer, claimed, self.brief.text(claimed, task, self.reports.last(claimed)))
        except Exception:
            self.workers.save(self.workers.find(claimed.id).review_failed(self.time_source.seconds(), task.id), Actor.system())
            raise
        self.steps.started(reviewing, claimed.mention())

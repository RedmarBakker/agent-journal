import time

from journal.events.listener import Listener
from journal.events.rows.worker_review_requested import WorkerReviewRequested
from journal.features.reviewing.support.review_brief import ReviewBrief
from journal.features.reviewing.support.reviewer_dispatch import ReviewerDispatch
from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class ReviewerStart(Listener[WorkerReviewRequested]):
    """A worker's work sent to review is reviewed by a reviewer the journal sends itself, handed the brief, the proofs and the report; a reviewer that cannot be sent hands the work back to the agent that sent the worker at once, so it is never left waiting."""

    def __init__(self, workers: Workers, tasks: Tasks, brief: ReviewBrief, dispatch: ReviewerDispatch) -> None:
        self.workers, self.tasks, self.brief, self.dispatch = workers, tasks, brief, dispatch

    def handle(self, event: WorkerReviewRequested) -> None:
        worker = self.workers.find(event.worker.id)
        task = self.tasks.find(self.tasks.holder_task_ids(Ref.build(worker))[0])
        try:
            self.dispatch.sent(worker, self.brief.text(worker, task, event.report))
        except Exception:
            self.workers.save(self.workers.find(worker.id).review_failed(time.time(), task.id), Actor.system())
            raise

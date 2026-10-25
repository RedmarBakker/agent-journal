import time

from journal.events.listener import Listener
from journal.events.rows.reviewer_ended import ReviewerEnded
from journal.features.reviewing.support.reviewer_dispatch import ReviewerDispatch
from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class ReviewHandback(Listener[ReviewerEnded]):
    """A reviewer that ended without its report, or ran past its limit, hands the work it reviewed back to the agent that sent the worker, for that agent's own check."""

    def __init__(self, workers: Workers, tasks: Tasks, dispatch: ReviewerDispatch) -> None:
        self.workers, self.tasks, self.dispatch = workers, tasks, dispatch

    def handle(self, event: ReviewerEnded) -> None:
        worker = self.workers.find(self.dispatch.reviewed(event.row_id).id)
        if worker.in_review:
            self.workers.save(worker.review_failed(time.time(), self.tasks.last_task_id(Ref.build(worker))), Actor.system())

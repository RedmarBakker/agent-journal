from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.worker_review_failed import WorkerReviewFailed
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.features.reviewing.reviewing_nudges import ReviewingNudges


class ReviewingConduct(Conduct):
    """The reviewing feature's conduct toward the agent that sent a worker, in every state: the reviewer's report on that worker's work is informed as it comes, with each point and the tests run, and a reviewer that ended without one hands the work back for the agent's own check."""

    def on_worker_reviewed(self, event: WorkerReviewed, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(ReviewingNudges.WORK_REVIEWED.create(reviewer=event.reviewer, n=event.worker.id, name=event.worker.name, task=event.task, report=event.report))

    def on_worker_review_failed(self, event: WorkerReviewFailed, settings: Settings) -> Transition:
        if event.worker.is_other_dispatcher(event.session):
            return self.none()
        return self.none(ReviewingNudges.REVIEW_FAILED.create(n=event.worker.id, name=event.worker.name, task=event.task))

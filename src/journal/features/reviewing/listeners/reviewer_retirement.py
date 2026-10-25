from journal.events.listener import Listener
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.features.reviewing.support.review_queue import ReviewQueue
from journal.features.reviewing.support.reviewer_runner import ReviewerRunner
from journal.repositories.reviewers import Reviewers
from journal.support.actor import Actor


class ReviewerRetirement(Listener[WorkerReviewed]):
    """A reviewer's report marks it reviewed, idle for the next review, and stops its process; the next review in the queue goes to it at once."""

    def __init__(self, reviewers: Reviewers, runner: ReviewerRunner, queue: ReviewQueue) -> None:
        self.reviewers, self.runner, self.queue = reviewers, runner, queue

    def handle(self, event: WorkerReviewed) -> None:
        for reviewer in self.reviewers.session_checkers(event.reviewer_session):
            self.reviewers.save(reviewer.reviewed(), Actor.system())
            self.runner.stop(reviewer)
        self.queue.assigned(event.environment_id)

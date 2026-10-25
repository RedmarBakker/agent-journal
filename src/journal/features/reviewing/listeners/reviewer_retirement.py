from journal.events.listener import Listener
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.features.reviewing.support.reviewer_runner import ReviewerRunner
from journal.repositories.reviewers import Reviewers
from journal.support.actor import Actor


class ReviewerRetirement(Listener[WorkerReviewed]):
    """A reviewer's report marks it reviewed, idle for the next review, and stops its process."""

    def __init__(self, reviewers: Reviewers, runner: ReviewerRunner) -> None:
        self.reviewers, self.runner = reviewers, runner

    def handle(self, event: WorkerReviewed) -> None:
        for reviewer in self.reviewers.session_reviewer(event.reviewer_session):
            self.reviewers.save(reviewer.reviewed(), Actor.system())
            self.runner.stop(reviewer)

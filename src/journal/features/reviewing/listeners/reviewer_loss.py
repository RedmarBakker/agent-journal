from journal.events.listener import Listener
from journal.events.rows.reviewer_ended import ReviewerEnded
from journal.features.reviewing.support.review_queue import ReviewQueue


class ReviewerLoss(Listener[ReviewerEnded]):
    """A reviewer that ended without a report leaves the reviewers, and the next review in the queue goes to another, or to a first one when none is left."""

    def __init__(self, queue: ReviewQueue) -> None:
        self.queue = queue

    def handle(self, event: ReviewerEnded) -> None:
        self.queue.assigned(event.environment_id)

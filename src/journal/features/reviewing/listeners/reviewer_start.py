from journal.events.listener import Listener
from journal.events.rows.worker_review_requested import WorkerReviewRequested
from journal.features.reviewing.support.review_queue import ReviewQueue


class ReviewerStart(Listener[WorkerReviewRequested]):
    """A worker's work sent to review joins the review queue, and the next review goes to a free reviewer at once."""

    def __init__(self, queue: ReviewQueue) -> None:
        self.queue = queue

    def handle(self, event: WorkerReviewRequested) -> None:
        self.queue.assigned(event.environment_id)

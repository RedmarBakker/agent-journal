from journal.events.listener import Listener
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.features.reviewing.support.review_report import ReviewReport
from journal.features.reviewing.support.review_steps import ReviewSteps


class ReviewReportSteps(Listener[WorkerReviewed]):
    """A reviewer's report is shown in its pane point by point, each passed or short, then whole, as it handed it to the agent."""

    def __init__(self, steps: ReviewSteps) -> None:
        self.steps = steps

    def handle(self, event: WorkerReviewed) -> None:
        self.steps.reported(event.environment_id, event.reviewer_session, event.worker, ReviewReport(event.report))

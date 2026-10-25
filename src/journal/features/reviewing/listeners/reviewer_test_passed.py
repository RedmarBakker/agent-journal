from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.reviewing.support.review_steps import ReviewSteps
from journal.features.shell.support.activity_label import ActivityLabel
from journal.repositories.reviewers import Reviewers


class ReviewerTestPassed(AgentListener[ToolFinished]):
    """A test a reviewer ran that ended well is shown passed in its pane."""

    is_worker_listener = True

    def __init__(self, reviewers: Reviewers, steps: ReviewSteps) -> None:
        self.reviewers, self.steps = reviewers, steps

    def handle(self, event: ToolFinished) -> None:
        for reviewer in self.reviewers.session_checkers(event.session):
            for command in ActivityLabel.test_runs(tuple(part.text for part in event.call.parts)):
                self.steps.test_passed(reviewer, command)

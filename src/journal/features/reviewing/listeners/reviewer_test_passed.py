from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.reviewing.support.review_steps import ReviewSteps
from journal.repositories.reviewers import Reviewers


class ReviewerTestPassed(AgentListener[ToolFinished]):
    """A test a reviewer ran that ended well is shown passed in its pane."""


    def __init__(self, reviewers: Reviewers, steps: ReviewSteps) -> None:
        self.reviewers, self.steps = reviewers, steps

    def handle(self, event: ToolFinished) -> None:
        for reviewer in self.reviewers.session_checkers(event.session):
            for command in event.call.test_runs():
                self.steps.test_passed(reviewer, command)

from journal.events.agent.tool_failed import ToolFailed
from journal.events.agent_listener import AgentListener
from journal.features.reviewing.support.review_steps import ReviewSteps
from journal.features.shell.support.activity_label import ActivityLabel
from journal.repositories.reviewers import Reviewers


class ReviewerTestFailed(AgentListener[ToolFailed]):
    """A test a reviewer ran that ended in an error is shown failed in its pane."""


    def __init__(self, reviewers: Reviewers, steps: ReviewSteps) -> None:
        self.reviewers, self.steps = reviewers, steps

    def handle(self, event: ToolFailed) -> None:
        for reviewer in self.reviewers.session_checkers(event.session):
            for command in ActivityLabel.test_runs(tuple(part.text for part in event.call.parts)):
                self.steps.test_failed(reviewer, command)

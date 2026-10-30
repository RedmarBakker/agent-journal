from journal.features.reviewing.support.reviewer_runner import ReviewerRunner
from journal.repositories.reviewers import Reviewers
from journal.repositories.scope import Scope
from tests.stories.builder.step_result import StepResult
from tests.stories.builder.story_agent import StoryAgent


class ReviewerSteps:
    """What a reviewer's runner does when its session ends without a report."""

    def reviewer_run_ends_without_a_report(self, agent: StoryAgent) -> StepResult:
        with self.app.container.get(Scope).environment(1):
            reviewer = self.app.container.get(Reviewers).find(agent.number)
            self.app.container.get(ReviewerRunner).ended(reviewer)
        return self.observed("the reviewer's run ends without a report", None, None)

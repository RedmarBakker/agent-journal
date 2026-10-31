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

    def an_old_reviewer_run_ends_after_its_row_is_reused(self, agent: StoryAgent) -> StepResult:
        with self.app.container.get(Scope).environment(1):
            reviewer = self.app.container.get(Reviewers).find(agent.number)
            old_run = reviewer.with_(token_hash="an earlier review run")
            self.app.container.get(ReviewerRunner).ended(old_run)
        return self.observed("an old reviewer run ends after its row is reused", None, None)

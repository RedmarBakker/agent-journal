from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PlanApproved(StateFixture):
    """The user approved the plan they made in the viewer, not yet started: story.plans.first, story.tasks.first and story.tasks.second."""

    stack = (Ready,)

    parent = UserDraftedPlan

    def steps(self, story) -> None:
        story.user_approves_plan(self.plans.first)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.APPROVED)

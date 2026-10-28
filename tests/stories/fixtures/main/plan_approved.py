from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PlanApproved(StateFixture):
    """The user approved the plan they made in the viewer, not yet started: start.plan, start.first_task and start.second_task."""

    stack = (Ready,)

    parent = UserDraftedPlan

    def steps(self, story) -> None:
        story.user_approves_plan(self.plan)

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.APPROVED)

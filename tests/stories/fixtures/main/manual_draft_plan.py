from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.draft_plan import DraftPlan
from tests.stories.fixtures.state_fixture import StateFixture


class ManualDraftPlan(StateFixture):
    """The agent gave up the plan building sequence its draft started, to build the draft step by step itself: start.plan."""

    stack = (Ready,)

    parent = DraftPlan

    def steps(self, story) -> None:
        story.agent_runs("sequence follow")
        story.agent_runs("sequence abandon --why 'the plan is built step by step right here' --sure")

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.DRAFT)
        story.expect_stack(Ready)

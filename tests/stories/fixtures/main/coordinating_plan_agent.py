from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.state_fixture import StateFixture


class CoordinatingPlanAgent(StateFixture):
    """An approved plan waits while its plan agent coordinates the work."""

    parent = PlanApproved
    stack = (CoordinatingPlans,)
    settings = ((PlansOptions.PLAN_AGENTS, True),)

    def steps(self, story) -> None:
        pass

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, CoordinatingPlans)

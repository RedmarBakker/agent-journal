from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class OrganizationHubPlanWithPlanAgents(OrganizationHubPlan):
    """An organization hub plan with plan agents enabled."""

    parent = OrganizationHubPlan
    settings = ((PlansOptions.PLAN_AGENTS, True),)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.agents.main, CoordinatingPlans)

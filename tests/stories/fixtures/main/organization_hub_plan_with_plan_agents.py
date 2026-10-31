from journal.features.plans.plans_options import PlansOptions
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class OrganizationHubPlanWithPlanAgents(OrganizationHubPlan):
    """An organization hub plan with plan agents enabled."""

    parent = OrganizationHubPlan
    settings = ((PlansOptions.PLAN_AGENTS, True),)

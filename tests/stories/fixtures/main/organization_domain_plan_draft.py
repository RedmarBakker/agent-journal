from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class OrganizationDomainPlanDraft(OrganizationHubPlan):
    """A draft plan has its first task assigned to the Alpha Domain."""

    parent = OrganizationHubPlan.parent
    settings = ((PlansOptions.PLAN_AGENTS, True),)
    stack = (CoordinatingPlans,)
    task_domain = "alpha"

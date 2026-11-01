from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class OrganizationDomainPlanDraft(OrganizationHubPlan):
    """A draft plan has its first task assigned to the Alpha Domain."""

    parent = OrganizationHubPlan.parent
    settings = ((PlansOptions.PLAN_AGENTS, True),)
    stack = (CoordinatingPlans,)
    task_domain = "alpha"

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.agents.main, CoordinatingPlans)

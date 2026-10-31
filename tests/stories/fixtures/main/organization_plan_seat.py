from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.organization.support.organization import Organization
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan
from tests.stories.fixtures.main.organization_setup import OrganizationSetup


class OrganizationPlanSeat(OrganizationHubPlan):
    """An approved organization plan has a planned Alpha task and a simulated OpenRig."""

    parent = OrganizationSetup
    settings = ((PlansOptions.PLAN_AGENTS, True),)
    task_domain = "alpha"

    def steps(self, story) -> None:
        story.app.container.get(Organization).reload()
        super().steps(story)
        story.configure_simulated_openrig()
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.APPROVED)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.agents.main, CoordinatingPlans)

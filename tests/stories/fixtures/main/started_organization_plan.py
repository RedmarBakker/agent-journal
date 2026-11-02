from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat


class StartedOrganizationPlan(OrganizationPlanSeat):
    """An approved organization plan has started on its simulated OpenRig."""

    parent = OrganizationPlanSeat
    settings = ()

    def steps(self, story) -> None:
        story.configure_simulated_openrig()
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)

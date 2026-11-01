from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat


class OrganizationPlanWithDomainSeats(OrganizationPlanSeat):
    """A started organization plan has all its generated Domain seats in its plan rig."""

    parent = OrganizationPlanSeat
    settings = ()

    def steps(self, story) -> None:
        plan = self.plans.first
        story.configure_simulated_openrig()
        runtime = story.app.container.get(SeatRuntime)
        story.agent_runs(story.agents.main, f"plan start {plan}").expect_command_passed()
        self.add_domain_seats(story, runtime)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)

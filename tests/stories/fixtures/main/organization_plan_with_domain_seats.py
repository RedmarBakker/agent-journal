from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.models.plan_state import PlanState
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from tests.stories.fixtures.main.started_organization_plan import StartedOrganizationPlan


class OrganizationPlanWithDomainSeats(StartedOrganizationPlan):
    """A started organization plan has all its generated Domain seats in its plan rig."""

    parent = StartedOrganizationPlan
    settings = ()

    def steps(self, story) -> None:
        runtime = story.app.container.get(SeatRuntime)
        self.add_domain_seats(story, runtime)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)

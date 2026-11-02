from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


class RestartedIdleMainWithOrganizationSeats(OrganizationPlanWithDomainSeats):
    """An idle main agent has a fresh journal runtime and a supervisor beside a seat with no native session ID."""

    parent = OrganizationPlanWithDomainSeats

    def steps(self, story) -> None:
        story.agent_stops(story.agents.main).expect_allowed(story.agents.main)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)

    def restore_on(self, story) -> None:
        super().restore_on(story)
        story.journal_restarts()
        story.organization_seat_has_no_native_session(self.plans.first, "plan")
        story.agent_supervisor_accepts_lines(story.agents.main)

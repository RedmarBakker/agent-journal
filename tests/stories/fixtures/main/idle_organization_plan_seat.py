from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


class IdleOrganizationPlanSeat(OrganizationPlanWithDomainSeats):
    """The Plan seat has handed off its first task and stopped between turns."""

    parent = OrganizationPlanWithDomainSeats

    def steps(self, story) -> None:
        story.agent_starts_plan_seat(story.agents.main, self.plans.first).expect_allowed(story.agents.main)
        story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview").expect_command_passed()
        story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"organization handoff {self.tasks.first} domain:alpha").expect_command_passed()
        story.agent_stops_plan_seat(story.agents.main, self.plans.first).expect_allowed(story.agents.main)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)

from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_plan_without_domain_seats import OrganizationPlanWithoutDomainSeats


class OrganizationDomainSeatStarted(OrganizationPlanWithoutDomainSeats):
    """An organization plan has handed its first task to a started Domain seat."""

    parent = OrganizationPlanWithoutDomainSeats
    settings = ()

    def steps(self, story) -> None:
        plan, task = story.plans.first, story.tasks.first
        handed = story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"organization handoff {task} domain:alpha",
        )
        handed.expect_command_passed()
        handed.expect_command_text(f"task {task} routed from plan to domain:alpha")
        domain = story.organization_seat_agent("domain:alpha")
        story.expect_openrig_seat_received(domain, story.plan_rig_name(plan), "domain:alpha", OrganizationSeatRouting.handoff_prompt)
        started = story.agent_starts_organization_seat(domain, "domain:alpha")
        started.expect_allowed(domain)
        story.expect_openrig_seat_environment(domain, "domain:alpha")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.organization_seat_agent("domain:alpha"), LeadingPlan, FollowingPlan)

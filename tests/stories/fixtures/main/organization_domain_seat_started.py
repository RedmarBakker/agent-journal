from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from tests.stories.fixtures.main.organization_plan_without_domain_seats import OrganizationPlanWithoutDomainSeats


class OrganizationDomainSeatStarted(OrganizationPlanWithoutDomainSeats):
    """An organization plan has handed its first task to a started Domain seat."""

    parent = OrganizationPlanWithoutDomainSeats

    def steps(self, story) -> None:
        plan, task = story.plans.first, story.tasks.first
        handed = story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"organization handoff {task} domain:alpha",
        )
        handed.expect_command_passed()
        handed.expect_command_text(f"task {task} routed from plan to domain:alpha")
        domain = story.organization_seat_agent("domain:alpha")
        story.expect_openrig_seat_received(domain, f"plan-{plan}", "domain:alpha", OrganizationSeatRouting.handoff_prompt)
        started = story.agent_starts_organization_seat(domain, "domain:alpha")
        started.expect_allowed(domain)
        story.expect_openrig_seat_environment(domain, "domain:alpha")

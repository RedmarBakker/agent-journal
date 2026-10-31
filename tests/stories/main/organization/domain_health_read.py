from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


@story(OrganizationPlanWithDomainSeats, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_domain_seat_can_read_this_journals_health_without_a_prompt(story):
    domain = story.organization_seat_agent("domain:alpha")
    started = story.agent_starts_organization_seat(domain, "domain:alpha")
    started.expect_allowed(domain)
    story.expect_openrig_seat_environment(domain, "domain:alpha")
    story.expect_openrig_seat_health_read(domain, "domain:alpha")
    checked = story.agent_uses_the_providers_tool(
        domain, "Bash", command=OrganizationSeatRouting.health_command,
    )
    checked.expect_allowed(domain)

    story.expect_stack(story.agents.subject, CoordinatingPlans, OrchestratingPlan)

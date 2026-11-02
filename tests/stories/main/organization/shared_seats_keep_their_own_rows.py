from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.shared_organization_domain_seat_started import SharedOrganizationDomainSeatStarted


@story(SharedOrganizationDomainSeatStarted, subject=AgentRole.MAIN)
def test_a_shared_domain_seat_starts_and_reads_without_taking_over_the_main_agent(story):
    rig = story.shared_rig_name(story.plans.first)
    domain = story.organization_seat_agent("domain:alpha", rig)
    result = story.agent_runs_as_organization_seat(domain, "domain:alpha", "environment overview", rig)
    result.expect_command_passed()
    story.expect_seat_has_its_own_environment(domain, "domain:alpha", rig)
    story.expect_agent_session_in_environment(story.agents.main, "main")
    story.expect_stack(story.agents.main, CoordinatingPlans)


@story(SharedOrganizationDomainSeatStarted, subject=AgentRole.MAIN)
def test_a_shared_read_only_role_starts_and_reads_without_taking_over_the_main_agent(story):
    rig = story.shared_rig_name(story.plans.first)
    role = story.organization_seat_agent("role:alpha/shared", rig)
    story.agent_starts_organization_seat(role, "role:alpha/shared", rig).expect_allowed(role)
    result = story.agent_runs_as_organization_seat(role, "role:alpha/shared", "environment overview", rig)
    result.expect_command_passed()
    story.expect_seat_has_its_own_environment(role, "role:alpha/shared", rig)
    story.expect_agent_session_in_environment(story.agents.main, "main")
    story.expect_stack(story.agents.main, CoordinatingPlans)

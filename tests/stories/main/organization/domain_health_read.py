from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.organization.support.rig_specs import RigSpecs
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_seat_started import OrganizationDomainSeatStarted


@story(OrganizationDomainSeatStarted, subject=AgentRole.MAIN)
def test_a_domain_seat_can_read_this_journals_health_without_a_prompt(story):
    domain = story.organization_seat_agent("domain:alpha")
    port = story.app.container.get(RigSpecs).journal_port()
    command = f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:{port}/journal/health'
    story.expect_openrig_seat_health_read(domain, "domain:alpha", command)
    checked = story.agent_uses_the_providers_tool(
        domain, "Bash", command=command,
    )
    checked.expect_allowed(domain)

    story.expect_stack(domain, LeadingPlan, FollowingPlan)

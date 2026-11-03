from journal.features.organization.support.rig_specs import RigSpecs
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_plan_seat import OrganizationPlanSeat


@story(OrganizationPlanSeat, subject=AgentRole.MAIN)
def test_a_plan_seat_runs_its_journal_health_check_without_a_prompt(story):
    plan = story.plans.first
    story.agent_runs(story.agents.main, f"plan start {plan}").expect_command_passed()
    story.agent_starts_plan_seat(story.agents.main, plan).expect_allowed(story.agents.main)

    port = story.app.container.get(RigSpecs).journal_port()
    command = f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:{port}/journal/health'
    story.expect_openrig_seat_health_read(story.agents.main, "plan", command)
    checked = story.agent_uses_the_providers_tool(story.agents.main, "Bash", command=command)
    checked.expect_allowed(story.agents.main)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)

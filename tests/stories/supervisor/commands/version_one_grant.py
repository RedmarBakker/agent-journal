from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.version_one_grant import VersionOneGrant


@story(VersionOneGrant, subject=AgentRole.SUPERVISOR)
def test_the_supervisor_runs_a_read_command_in_its_granted_plan_environment(story):
    result = story.supervisor_runs_read_command(story.agents.subject)
    result.expect_command_passed()
    result.expect_command_text("inspect service")
    story.expect_supervisor_grant_covers_plan(story.agents.subject, story.plans.first)
    result = story.supervisor_runs_read_command(story.agents.subject, "plan list")
    result.expect_command_passed()
    result.expect_command_text("started plan")
    story.expect_stack(story.agents.subject)

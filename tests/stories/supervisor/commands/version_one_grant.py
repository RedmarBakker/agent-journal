from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.supervisor.version_one_grant import VersionOneGrant


@story(VersionOneGrant, subject=AgentRole.SUPERVISOR)
def test_the_supervisor_runs_a_read_command_in_its_grant_environment(story):
    result = story.supervisor_runs_read_command(story.agents.subject, "task list")
    result.expect_command_passed()
    story.expect_supervisor_grant_covers_plan(story.agents.subject, story.plans.first)
    story.expect_stack(story.agents.subject)

from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_main_agent_has_no_work_mode_command(story):
    result = story.agent_runs(story.agents.subject, "mode show")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)

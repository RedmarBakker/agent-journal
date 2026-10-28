from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_command_reads_its_own_environments_rows_only(story):
    other = story.another_environment("other")
    story.agent_creates_task("the main task")
    story.session_starts_in(other, "s-other")
    story.agent_in_runs(other, "s-other", "task create 'the other task'")
    story.agent_runs("task list")
    story.expect_command_text("the main task")
    story.expect_command_text_without("the other task")
    story.agent_in_runs(other, "s-other", "task list")
    story.expect_command_text("the other task")
    story.expect_command_text_without("the main task")
    story.expect_stack(Ready)

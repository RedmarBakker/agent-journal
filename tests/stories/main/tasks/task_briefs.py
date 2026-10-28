from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_tasks_brief_is_written_anew(story):
    footer = story.agent_creates_briefed_task("the footer", "done when it stays at the bottom")
    story.agent_runs(f"task brief {footer} 'done when it stays at the bottom on every page'")
    story.expect_command_text(f"task {footer} brief written anew")
    story.expect_task(footer, brief="done when it stays at the bottom on every page")
    story.expect_stack(Ready)

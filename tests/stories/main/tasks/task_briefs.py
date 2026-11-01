from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_tasks_brief_is_written_anew(story):
    footer = story.agent_creates_briefed_task(story.agents.subject, "the footer", "done when it stays at the bottom")
    result = story.agent_runs(story.agents.subject, f"task brief {footer} 'done when it stays at the bottom on every page'")
    result.expect_command_text(f"task {footer} brief written anew")
    story.expect_task(footer, brief="done when it stays at the bottom on every page")
    story.expect_stack(story.agents.subject, Ready)

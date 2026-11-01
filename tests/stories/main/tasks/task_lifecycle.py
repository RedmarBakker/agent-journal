from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_task_is_created_started_logged_listed_and_completed_with_its_outcome(story):
    notes = story.agent_creates_briefed_task(story.agents.subject, "write the notes", "what and where")
    story.agent_runs(story.agents.subject, f"task start {notes}")
    story.agent_runs(story.agents.subject, f"task log {notes} 'half done'")
    result = story.agent_runs(story.agents.subject, "task list")
    result.expect_command_text("started  write the notes")
    story.agent_runs(story.agents.subject, f"task complete {notes} --how published")
    story.expect_task(notes, state=TaskState.COMPLETED, outcome="published")
    story.expect_task_logged(notes, "half done")
    story.expect_stack(story.agents.subject, Ready)

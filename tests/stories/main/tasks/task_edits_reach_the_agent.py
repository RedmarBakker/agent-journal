from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_user_editing_the_task_in_hand_is_told_to_the_agent(story):
    result = story.user_edits_task(story.tasks.started, "Write the footer with the copyright")
    result.expect_agent_told(story.agents.subject, TasksNudges.TASK_CHANGED, n=story.tasks.started)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_agent_editing_its_own_task_is_not_told_back(story):
    result = story.agent_runs(story.agents.subject, f"task edit {story.tasks.started} --title 'Write the footer and its links'")
    result.expect_agent_not_told(story.agents.subject, TasksNudges.TASK_CHANGED)
    story.expect_stack(story.agents.subject, Ready, Working)

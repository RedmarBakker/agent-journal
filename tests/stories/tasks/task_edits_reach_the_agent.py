from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.started_task import StartedTask


@story(StartedTask, end=[Ready, Working])
def test_the_user_editing_the_task_in_hand_is_told_to_the_agent(story):
    story.user_edits_task(story.start.started_task, "Write the footer with the copyright")
    story.expect_agent_told(TasksNudges.TASK_CHANGED, n=story.start.started_task)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedTask, end=[Ready, Working])
def test_the_agent_editing_its_own_task_is_not_told_back(story):
    story.agent_runs(f"task edit {story.start.started_task} --title 'Write the footer and its links'")
    story.expect_agent_not_told(TasksNudges.TASK_CHANGED)

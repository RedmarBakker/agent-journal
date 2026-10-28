from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.started_task import StartedTask


@story(StartedTask)
def test_a_task_blocked_on_another_is_taken_up_when_that_one_closes(story):
    header = story.agent_creates_task("the header")
    story.agent_runs(f"task block {header} --on task:{story.start.started_task}")
    story.expect_task(header, state=TaskState.BLOCKED)
    story.agent_runs(f"task complete {story.start.started_task} --how done")
    story.expect_task(header, state=TaskState.STARTED)
    story.expect_agent_told(TasksNudges.TASK_REOPENED, n=header)


@story(StartedTask, end=[Ready, Working])
def test_a_task_blocked_by_hand_opens_when_unblocked(story):
    logo = story.agent_creates_task("the logo")
    story.agent_runs(f"task block {logo} 'waits on the designer'")
    story.expect_task(logo, state=TaskState.BLOCKED)
    story.agent_runs(f"task unblock {logo}")
    story.expect_task(logo, state=TaskState.OPEN)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)

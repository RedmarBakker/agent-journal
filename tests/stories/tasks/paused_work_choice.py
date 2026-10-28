from tests.stories.fixtures.paused_work_choice import PausedWorkChoice
from journal.features.tasks.states.choosing_paused_work import ChoosingPausedWork
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.started_task import StartedTask


@story(PausedWorkChoice, end=[Ready, Working])
def test_resuming_the_paused_task_ends_the_choice(story):
    story.agent_runs(f"task resume {story.start.started_task}")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_task(story.start.next_open, state=TaskState.OPEN)


@story(PausedWorkChoice, end=[Ready, Working])
def test_skipping_the_paused_task_starts_the_open_one(story):
    story.agent_runs("task skip-paused")
    story.agent_stops()
    story.expect_task(story.start.next_open, state=TaskState.STARTED)
    story.expect_task(story.start.started_task, state=TaskState.PAUSED)

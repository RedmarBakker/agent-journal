from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(StartedTask, mode=BUILDER_MODE)
@setting(TasksOptions.LOG_AGE_LIMIT, 10)
def test_a_stop_after_the_log_age_limit_asks_for_a_log_first(story):
    story.time_passes(minutes=story.setting(TasksOptions.LOG_AGE_LIMIT) + 1)
    story.agent_stops()
    story.expect_refused(TasksNudges.STOP_LOG_REQUEST)
    story.agent_runs(f"task log {story.start.started_task} 'the footer has its links'")
    story.agent_stops()
    story.expect_refused(TasksNudges.TASK_CONTINUATION)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE)
@setting(TasksOptions.FIRST_DELAY, 2)
def test_a_stop_after_enough_edits_asks_for_a_log_first(story):
    story.repeat(int(story.setting(TasksOptions.FIRST_DELAY)), lambda: story.agent_writes("a.py"))
    story.agent_stops()
    story.expect_refused(TasksNudges.STOP_LOG_REQUEST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_completed_task_leaves_the_hand_and_the_stop_goes_through(story):
    story.agent_runs(f"task complete {story.start.started_task} --how done")
    story.agent_stops()
    story.expect_allowed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_with_nothing_in_hand_and_nothing_open_the_stop_goes_through(story):
    story.agent_stops()
    story.expect_allowed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(TasksOptions.AUTO, False)
def test_an_open_task_without_auto_mode_lets_the_stop_go_through(story):
    task = story.agent_creates_task("the header")
    story.agent_stops()
    story.expect_allowed()
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(Ready)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_new_session_start_names_the_task_in_hand(story):
    story.agent_starts_a_session()
    story.expect_agent_told(TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE)
@setting(TasksOptions.AUTO, False)
def test_a_paused_task_is_named_once_at_the_stop_with_auto_mode_off(story):
    story.agent_runs(f"task pause {story.start.started_task} 'the header first'")
    story.agent_stops()
    story.expect_refused(TasksNudges.PAUSED_TASKS)
    story.agent_stops()
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.PAUSED)
    story.expect_stack(Ready)

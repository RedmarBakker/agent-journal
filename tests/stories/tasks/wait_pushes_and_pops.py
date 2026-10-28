from tests.stories.fixtures.await_with_open_work import AwaitWithOpenWork
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.started_task import StartedTask


@story(AwaitWithOpenWork, end=[Ready, Working, ExternalWait])
def test_a_wait_with_a_task_in_progress_lets_the_stop_go_through(story):
    story.agent_stops()
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(AwaitWithOpenWork, end=[Ready, Working, ExternalWait])
def test_a_task_started_during_a_wait_is_carried_on_with_once(story):
    story.agent_runs(f"task test {story.start.started_task}")
    story.agent_stops()
    story.expect_refused(TasksNudges.WAIT_NEXT_TASK, n=story.start.next_open)
    story.agent_stops()
    story.expect_allowed()


@story(StartedTask, end=[Ready, Working])
def test_working_again_ends_the_wait(story):
    story.agent_runs("await 'the build' --until false")
    story.agent_writes("a.py")
    story.expect_stack(Ready, Working)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)


@story(StartedTask, end=[Ready, Working])
def test_a_wait_that_names_nothing_to_wait_on_is_refused(story):
    story.agent_runs("await 'the build'")
    story.expect_command_refused()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)

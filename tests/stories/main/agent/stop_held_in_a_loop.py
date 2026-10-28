from journal.engine.safety_conduct import PANIC_REFUSAL_COUNT
from journal.engine.states.panicking import Panicking
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.looped_stops import LoopedStops
from tests.stories.fixtures.main.started_task import StartedTask


@story(LoopedStops, mode=BUILDER_MODE)
def test_the_stop_after_the_loop_is_named_goes_through(story):
    story.agent_stops()
    story.expect_allowed()
    story.expect_agent_told_nothing()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, Panicking)


@story(LoopedStops, mode=BUILDER_MODE)
def test_a_tool_use_after_the_loop_brings_the_work_back(story):
    story.agent_reads()
    story.expect_allowed()
    story.expect_stack(Ready, Working)


@story(LoopedStops, mode=BUILDER_MODE)
def test_the_users_prompt_after_the_loop_brings_the_work_back(story):
    story.agent_is_prompted("go on with the footer")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(LoopedStops, mode=BUILDER_MODE)
def test_a_panic_report_goes_through_while_panicking(story):
    story.agent_runs("panic report")
    story.expect_command_passed()
    story.expect_stack(Ready, Working, Panicking)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_tool_use_between_held_stops_starts_the_count_again(story):
    story.repeat(PANIC_REFUSAL_COUNT - 1, story.agent_stops)
    story.agent_reads()
    story.repeat(PANIC_REFUSAL_COUNT - 1, story.agent_stops)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)

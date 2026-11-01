from journal.engine.safety_conduct import PANIC_REFUSAL_COUNT
from journal.engine.states.panicking import Panicking
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.looped_stops import LoopedStops
from tests.stories.fixtures.main.started_task import StartedTask


@story(LoopedStops, subject=AgentRole.MAIN)
def test_the_stop_after_the_loop_is_named_goes_through(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    result.expect_agent_told_nothing(story.agents.subject)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, Panicking)


@story(LoopedStops, subject=AgentRole.MAIN)
def test_a_tool_use_after_the_loop_brings_the_work_back(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, Working)


@story(LoopedStops, subject=AgentRole.MAIN)
def test_the_users_prompt_after_the_loop_brings_the_work_back(story):
    story.agent_is_prompted(story.agents.subject, "go on with the footer")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(LoopedStops, subject=AgentRole.MAIN)
def test_a_panic_report_goes_through_while_panicking(story):
    result = story.agent_runs(story.agents.subject, "panic report")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready, Working, Panicking)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_tool_use_between_held_stops_starts_the_count_again(story):
    story.repeat(PANIC_REFUSAL_COUNT - 1, lambda: story.agent_stops(story.agents.subject))
    story.agent_reads(story.agents.subject)
    story.repeat(PANIC_REFUSAL_COUNT - 1, lambda: story.agent_stops(story.agents.subject))
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)

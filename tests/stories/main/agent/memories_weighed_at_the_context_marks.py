from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.context_mark_task import ContextMarkTask
from tests.stories.fixtures.main.started_task import StartedTask

FIRST, SECOND = MemoryThresholds.CONTEXT[0], MemoryThresholds.CONTEXT[1]


@story(ContextMarkTask, mode=BUILDER_MODE)
def test_at_the_mark_writes_wait_while_reads_and_journal_commands_go_through(story):
    story.agent_writes("footer.py")
    story.expect_refused(MemoryNudges.DECISION_EDIT_BLOCK)
    story.agent_reads()
    story.expect_allowed()
    story.agent_runs_in_the_shell("journal task list")
    story.expect_allowed()
    story.expect_stack(Ready, Working, WeighingMemories)


@story(ContextMarkTask, mode=BUILDER_MODE)
def test_skipping_at_the_mark_ends_the_weighing(story):
    story.agent_runs("memory skip 'nothing new to keep'")
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(ContextMarkTask, mode=BUILDER_MODE)
def test_a_stop_at_the_mark_is_refused_with_the_mark(story):
    story.agent_stops()
    story.expect_refused(MemoryNudges.UNDECIDED_STOP, percent=FIRST)
    story.expect_stack(Ready, Working, WeighingMemories)


@story(ContextMarkTask, mode=BUILDER_MODE)
def test_the_next_mark_asks_again_once_the_first_was_decided(story):
    story.agent_runs("memory skip 'nothing new to keep'")
    story.agent_consumes_context(SECOND)
    story.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=SECOND)
    story.expect_stack(Ready, Working, WeighingMemories)


@story(ContextMarkTask, mode=BUILDER_MODE)
def test_a_mark_decided_is_not_asked_again_at_the_same_reading(story):
    story.agent_runs("memory skip 'nothing new to keep'")
    story.agent_consumes_context(FIRST)
    story.expect_agent_not_told(MemoryNudges.CONTEXT_DECISION)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_reading_past_two_marks_asks_for_the_highest_only(story):
    story.agent_consumes_context(SECOND)
    story.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=SECOND)
    story.expect_agent_not_told(MemoryNudges.CONTEXT_DECISION, percent=FIRST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, WeighingMemories)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_reading_below_the_first_mark_asks_nothing(story):
    story.agent_consumes_context(FIRST - 1)
    story.expect_agent_not_told(MemoryNudges.CONTEXT_DECISION)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)

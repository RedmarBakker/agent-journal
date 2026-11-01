from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from journal.providers.codex import Codex
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.main.context_mark_task import ContextMarkTask
from tests.stories.fixtures.main.started_task import StartedTask

FIRST, SECOND = MemoryThresholds.CONTEXT[0], MemoryThresholds.CONTEXT[1]


@story(ContextMarkTask, subject=AgentRole.MAIN)
def test_at_the_mark_writes_wait_while_reads_and_journal_commands_go_through(story):
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, MemoryNudges.DECISION_EDIT_BLOCK)
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal task list")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, Working, WeighingMemories)


@story(ContextMarkTask, subject=AgentRole.MAIN)
def test_skipping_at_the_mark_ends_the_weighing(story):
    story.agent_runs(story.agents.subject, "memory skip 'nothing new to keep'")
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(ContextMarkTask, subject=AgentRole.MAIN)
def test_a_stop_at_the_mark_is_refused_with_the_mark(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, MemoryNudges.UNDECIDED_STOP, percent=FIRST)
    story.expect_stack(story.agents.subject, Ready, Working, WeighingMemories)


@story(ContextMarkTask, subject=AgentRole.MAIN)
def test_the_next_mark_asks_again_once_the_first_was_decided(story):
    story.agent_runs(story.agents.subject, "memory skip 'nothing new to keep'")
    result = story.agent_consumes_context(story.agents.subject, SECOND)
    result.expect_agent_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION, percent=SECOND)
    story.expect_stack(story.agents.subject, Ready, Working, WeighingMemories)


@story(ContextMarkTask, subject=AgentRole.MAIN)
def test_a_mark_decided_is_not_asked_again_at_the_same_reading(story):
    story.agent_runs(story.agents.subject, "memory skip 'nothing new to keep'")
    result = story.agent_consumes_context(story.agents.subject, FIRST)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_reading_past_two_marks_asks_for_the_highest_only(story):
    result = story.agent_consumes_context(story.agents.subject, SECOND)
    result.expect_agent_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION, percent=SECOND)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION, percent=FIRST)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, WeighingMemories)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_reading_below_the_first_mark_asks_nothing(story):
    result = story.agent_consumes_context(story.agents.subject, FIRST - 1)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
@provider(Codex)
def test_a_codex_session_whose_rollout_reaches_a_mark_weighs_its_memories_before_it_writes(story):
    result = story.agent_consumes_context(story.agents.subject, FIRST)
    result.expect_agent_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION, percent=FIRST)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, MemoryNudges.DECISION_EDIT_BLOCK)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, WeighingMemories)

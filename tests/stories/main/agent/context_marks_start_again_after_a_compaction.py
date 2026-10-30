from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.context_mark_task import ContextMarkTask

FIRST = MemoryThresholds.CONTEXT[0]


@story(ContextMarkTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_after_a_compaction_the_first_mark_asks_again(story):
    story.agent_runs(story.agents.subject, "memory skip 'nothing new to keep'")
    story.context_is_compacted()
    story.agent_looks_at_the_overview(story.agents.subject)
    story.agent_consumes_context(story.agents.subject, 1)
    result = story.agent_consumes_context(story.agents.subject, FIRST)
    result.expect_agent_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION, percent=FIRST)
    story.expect_stack(story.agents.subject, Ready, Working, WeighingMemories)


@story(ContextMarkTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_lower_reading_starts_the_marks_again_without_a_compaction(story):
    story.agent_runs(story.agents.subject, "memory skip 'nothing new to keep'")
    story.agent_consumes_context(story.agents.subject, 1)
    result = story.agent_consumes_context(story.agents.subject, FIRST)
    result.expect_agent_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION, percent=FIRST)
    story.expect_stack(story.agents.subject, Ready, Working, WeighingMemories)

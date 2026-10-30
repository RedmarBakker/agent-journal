from journal.engine.states.void import Void
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent

FIRST_MARK = MemoryThresholds.CONTEXT[0]


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagents_context_reading_never_asks_anyone_to_weigh_memories(story):
    result = story.agent_consumes_context(story.agents.subject, FIRST_MARK)
    result.expect_agent_not_told(story.agents.subject, MemoryNudges.CONTEXT_DECISION)
    story.expect_stack(story.agents.main, Ready)
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_a_subagents_tool_use_never_ends_the_main_agents_wait(story):
    story.agent_runs(story.agents.main, "task create 'the footer' --start")
    story.agent_runs(story.agents.main, "await 'the build of the footer' --until false")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.main, Ready, Working, ExternalWait)
    story.expect_stack(story.agents.subject, Void, Researching)

from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.memory.memory_nudges import MemoryNudges
from tests.scenarios.builder.stack_states import IDLE, WEIGHING_MEMORIES
from tests.scenarios.builder.story_values import scenario, values
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
@values([50, 80, 90])
def test_each_context_mark_holds_writes_until_the_memories_are_weighed(scenario, value):
    scenario.agent_consumes_context(value)
    scenario.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=value)
    scenario.agent_writes("a.py")
    scenario.expect_refused(MemoryNudges.DECISION_EDIT_BLOCK)
    scenario.agent_runs("memory skip 'nothing new to keep'")
    scenario.agent_writes("a.py")
    scenario.expect_allowed()


@scenario(AgentAtWork)
def test_a_memory_added_at_the_mark_is_shown_at_the_next_session_start(scenario):
    scenario.agent_consumes_context(50)
    scenario.agent_adds_memory("the footer links come from the settings", 7)
    scenario.agent_writes("a.py")
    scenario.expect_allowed()

    scenario.second_session_starts()
    scenario.expect_agent_told(BriefingNudges.ENVIRONMENT_MEMORIES)


@scenario(AgentAtWork, end=[IDLE, WEIGHING_MEMORIES])
def test_a_stop_at_the_mark_is_held_until_the_memories_are_weighed(scenario):
    scenario.agent_consumes_context(50)
    scenario.agent_stops()
    scenario.expect_refused(MemoryNudges.UNDECIDED_STOP)

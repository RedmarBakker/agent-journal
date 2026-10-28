from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.memory.memory_nudges import MemoryNudges
from tests.scenarios.builder.story_values import starts_from
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@starts_from(TaskInHand)
def test_at_the_fifty_percent_mark_writes_wait_for_the_memories(scenario):
    scenario.context_reaches(50)
    scenario.agent_reads()
    scenario.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=50)
    scenario.agent_writes("a.py")
    scenario.expect_refused(MemoryNudges.DECISION_EDIT_BLOCK)
    scenario.agent_reads()
    scenario.expect_allowed()
    scenario.agent_runs("memory skip 'nothing to keep'")
    scenario.agent_writes("a.py")
    scenario.expect_allowed()


@starts_from(TaskInHand)
def test_after_a_compaction_the_overview_comes_first(scenario):
    scenario.context_is_compacted()
    scenario.agent_writes("a.py")
    scenario.expect_refused(BriefingNudges.OVERVIEW_FIRST)
    scenario.agent_looks_at_the_overview()
    scenario.agent_writes("a.py")
    scenario.expect_allowed()

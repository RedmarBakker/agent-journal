from journal.features.briefing.briefing_nudges import BriefingNudges
from tests.scenarios.builder.stack_states import IDLE, READING_OVERVIEW
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@scenario(TaskInHand)
def test_after_a_compaction_the_overview_comes_first(scenario):
    scenario.context_is_compacted()
    scenario.agent_writes("a.py")
    scenario.expect_refused(BriefingNudges.OVERVIEW_FIRST)
    scenario.agent_looks_at_the_overview()
    scenario.agent_runs(f"task log {scenario.task_in_hand} 'back after the compaction'")
    scenario.agent_writes("a.py")
    scenario.expect_allowed()


@scenario(AgentAtWork, end=[IDLE, READING_OVERVIEW])
def test_a_compaction_lowers_each_memory_by_one_and_shows_them_again(scenario):
    memory = scenario.agent_adds_memory("the footer links come from the settings", 5)
    scenario.context_is_compacted()
    scenario.expect_agent_told(BriefingNudges.ENVIRONMENT_MEMORIES)
    scenario.expect_row("memories", memory, {"weight": 4})

from journal.features.briefing.briefing_nudges import BriefingNudges
from tests.scenarios.builder.story_values import starts_from
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@starts_from(TaskInHand)
def test_a_new_session_takes_over_the_agent_with_its_task(scenario):
    scenario.second_session_starts()
    scenario.expect_agent_told(BriefingNudges.TAKEOVER)
    scenario.expect_agent_session("s2")
    scenario.expect_task(1, state="started")

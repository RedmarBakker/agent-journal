from journal.features.sequences.sequences_nudges import SequencesNudges
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
def test_a_sequence_is_followed_step_by_step_to_its_end(scenario):
    release = scenario.agent_creates_sequence("release", "raise the version | push the tag")
    scenario.agent_runs(f"sequence run {release}")
    scenario.expect_agent_told(SequencesNudges.PENDING_STEP, step=1)
    scenario.agent_runs("sequence follow")
    scenario.agent_runs("sequence next")
    scenario.expect_agent_told(SequencesNudges.PENDING_STEP, step=2)
    scenario.agent_runs("sequence follow")
    scenario.agent_runs("sequence next")
    scenario.expect_agent_told(SequencesNudges.SEQUENCE_ENDED)

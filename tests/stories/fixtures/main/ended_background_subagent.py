from journal.features.tasks.states.ready import Ready
from journal.models.subagent_state import SubagentState
from journal.support.card_outcome import CardOutcome
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER

MAPPER = "r1"
MAPPED_FILE = "src/journal/features/shell/chain.py"


class EndedBackgroundSubagent(StateFixture):
    """The agent sent a researcher in the background to map one file, and it ended: its session is MAPPER."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.agent_sends_subagent_in_the_background(story.agents.main, RESEARCHER, f"map {MAPPED_FILE}", MAPPER)
        story.subagent_ends(MAPPER)

    def expected(self, story) -> None:
        story.expect_dispatch_card(active=False, state=SubagentState.FINISHED.value, outcome=str(CardOutcome.PASSED))

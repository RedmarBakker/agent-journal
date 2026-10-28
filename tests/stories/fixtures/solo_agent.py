from journal.features.workers.states.soloing import Soloing
from journal.features.workers.workers_options import SOLO_MODE, WorkersOptions
from tests.stories.fixtures.briefed_task import BriefedTask
from tests.stories.fixtures.state_fixture import StateFixture


class SoloAgent(StateFixture):
    """The user switched the agent to solo mode with the briefed task open."""

    stack = (Soloing,)

    parent = BriefedTask

    settings = ((WorkersOptions.MODE, SOLO_MODE),)

    def steps(self, story) -> None:
        story.agent_reads()

    def expected(self, story) -> None:
        story.expect_stack(Soloing)

from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.fixtures.briefed_task import BriefedTask
from tests.stories.fixtures.state_fixture import StateFixture


class OrchestratorWithOpenTask(StateFixture):
    """The user switched the agent to orchestrator mode with the briefed task open and no worker on it."""

    stack = (Orchestrating,)

    parent = BriefedTask

    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        story.agent_reads()

    def expected(self, story) -> None:
        story.expect_stack(Orchestrating)

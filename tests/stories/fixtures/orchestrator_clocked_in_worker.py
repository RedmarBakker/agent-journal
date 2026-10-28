from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.fixtures.clocked_in_worker import ClockedInWorker
from tests.stories.fixtures.state_fixture import StateFixture


class OrchestratorClockedInWorker(StateFixture):
    """The user switched the agent that waits on its clocked-in worker to orchestrator mode."""

    stack = (Orchestrating, ExternalWait)

    parent = ClockedInWorker

    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        story.agent_reads()

    def expected(self, story) -> None:
        story.expect_stack(Orchestrating, ExternalWait)

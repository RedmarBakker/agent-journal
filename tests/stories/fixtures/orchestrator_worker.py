from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.fixtures.working_worker import WorkingWorker
from tests.stories.fixtures.state_fixture import StateFixture


class OrchestratorWorker(StateFixture):
    """The user switched the agent that waited on its clocked-in worker to orchestrator mode, which leaves the wait: the worker is out and the agent awaits nothing."""

    stack = (Orchestrating,)

    parent = WorkingWorker

    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        story.agent_reads()

    def expected(self, story) -> None:
        story.expect_stack(Orchestrating)

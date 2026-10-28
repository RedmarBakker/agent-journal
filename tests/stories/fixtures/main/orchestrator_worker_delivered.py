from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


class OrchestratorWorkerDelivered(StateFixture):
    """The user switched the agent whose worker's work waits for its check to orchestrator mode."""

    stack = (Orchestrating,)

    parent = WorkerDelivered

    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        story.agent_reads()

    def expected(self, story) -> None:
        story.expect_stack(Orchestrating)

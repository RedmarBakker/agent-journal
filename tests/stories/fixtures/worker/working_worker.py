from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.working_task import WorkingTask
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.state_fixture import StateFixture


class WorkingWorker(StateFixture):
    """The worker the agent sent clocked in and works in its own working state, while the agent waits on it."""

    stack = (Ready, ExternalWait)

    parent = DispatchedWorker

    def steps(self, story) -> None:
        story.agent_clocks_in(story.agents.workers.first())

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.READY)
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)

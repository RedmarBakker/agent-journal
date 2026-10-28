from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.working_task import WorkingTask
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.state_fixture import StateFixture


class WorkingWorker(StateFixture):
    """The worker the agent sent clocked in and works in its own working state, while the agent waits on it."""

    stack = (Ready, ExternalWait)

    parent = DispatchedWorker

    def steps(self, story) -> None:
        story.worker_clocks_in(self.worker)

    def expected(self, story) -> None:
        story.expect_worker(self.worker, state=WorkerState.READY)
        story.expect_worker_stack(self.worker, Void, WorkingTask)

from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.worker.working_worker import WorkingWorker


class TwoWorkers(StateFixture):
    """The agent sent a second worker on a second briefed task beside the working one, and it clocked in too: start.peer and start.peer_task."""

    stack = (Ready, ExternalWait)

    parent = WorkingWorker

    def steps(self, story) -> None:
        self.peer_task = story.agent_creates_briefed_task("the printer", "- prints each rule")
        self.peer = story.agent_dispatches_worker("Mr. Babbage", self.peer_task)
        story.worker_session_starts(self.peer)
        story.worker_clocks_in(self.peer)

    def expected(self, story) -> None:
        story.expect_worker(self.peer, state=WorkerState.READY)
        story.expect_task(self.peer_task, delegated=True)

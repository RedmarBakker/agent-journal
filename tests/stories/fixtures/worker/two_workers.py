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
        self.peer_task = story.agent_creates_briefed_task(story.agents.subject, "the printer", "- prints each rule")
        self.peer = story.agent_dispatches_worker(story.agents.subject, "Mr. Babbage", self.peer_task)
        story.agent_starts_a_session(story.agents.workers.get(self.peer))
        story.agent_clocks_in(story.agents.workers.get(self.peer))

    def expected(self, story) -> None:
        story.expect_worker(self.peer, state=WorkerState.READY)
        story.expect_task(self.peer_task, delegated=True)

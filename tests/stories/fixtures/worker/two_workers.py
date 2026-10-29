from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.worker.working_worker import WorkingWorker


class TwoWorkers(StateFixture):
    """The agent sent a second worker on a second briefed task beside the working one, and it clocked in too: story.agents.workers.second() and story.tasks.peer."""

    stack = (Ready, ExternalWait)

    parent = WorkingWorker

    def steps(self, story) -> None:
        self.tasks.peer = story.agent_creates_briefed_task(story.agents.main, "the printer", "- prints each rule")
        self.workers.second = story.agent_dispatches_worker(story.agents.main, "Mr. Babbage", self.tasks.peer)
        story.agent_starts_a_session(story.agents.workers.second())
        story.agent_clocks_in(story.agents.workers.second())

    def expected(self, story) -> None:
        story.expect_worker(self.workers.second, state=WorkerState.READY)
        story.expect_task(self.tasks.peer, delegated=True)

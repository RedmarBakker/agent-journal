from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.briefed_task import BriefedTask
from tests.stories.fixtures.state_fixture import StateFixture


class DispatchedWorker(StateFixture):
    """The agent sent a worker on the briefed task and waits on it; the worker's session started but it has not clocked in: story.agents.workers.first()."""

    stack = (Ready, ExternalWait)

    parent = BriefedTask

    def steps(self, story) -> None:
        self.workers.first = story.agent_dispatches_worker(story.agents.main, "Lady Lovelace", self.tasks.briefed)
        story.agent_starts_a_session(story.agents.workers.first())

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.DISPATCHED)
        story.expect_task(self.tasks.briefed, delegated=True)

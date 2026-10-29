from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.briefed_task import BriefedTask
from tests.stories.fixtures.state_fixture import StateFixture


class DispatchedWorker(StateFixture):
    """The agent sent a worker on the briefed task and waits on it; the worker's session started but it has not clocked in: start.worker."""

    stack = (Ready, ExternalWait)

    parent = BriefedTask

    def steps(self, story) -> None:
        self.worker = story.agent_dispatches_worker(story.agents.subject, "Lady Lovelace", self.briefed)
        story.agent_starts_a_session(story.agents.workers.get(self.worker))

    def expected(self, story) -> None:
        story.expect_worker(self.worker, state=WorkerState.DISPATCHED)
        story.expect_task(self.briefed, delegated=True)

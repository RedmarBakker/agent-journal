from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.briefed_task import BriefedTask
from tests.stories.fixtures.state_fixture import StateFixture


class ClockedInWorker(StateFixture):
    """The agent sent a worker on the briefed task, the worker clocked in, and the agent waits on it: start.worker and start.briefed."""

    stack = (Ready, ExternalWait)

    parent = BriefedTask

    def steps(self, story) -> None:
        self.worker = story.agent_dispatches_worker("Lady Lovelace", self.briefed)
        story.worker_clocks_in(self.worker)

    def expected(self, story) -> None:
        story.expect_stack(Ready, ExternalWait)

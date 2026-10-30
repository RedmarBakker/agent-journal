from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.worker.working_worker import WorkingWorker


class IdleWorker(StateFixture):
    """The working worker reported instead of clocking out, so it is idle for its next job: story.agents.workers.first()."""

    stack = (Ready,)

    parent = WorkingWorker

    def steps(self, story) -> None:
        story.agent_runs(story.agents.workers.first(), f"worker report {self.workers.first} 'the parser is half done'")

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.REPORTED)

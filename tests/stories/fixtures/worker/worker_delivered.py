from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.worker.working_worker import WorkingWorker


class WorkerDelivered(StateFixture):
    """A worker sent on the open task clocked in, proved both points and clocked out, its work waiting for the agent's check: story.agents.workers.first()."""

    stack = (Ready,)

    parent = WorkingWorker

    def steps(self, story) -> None:
        story.agent_proves(story.agents.workers.first(), 1, "parser.py:12, test_reads passes")
        story.agent_proves(story.agents.workers.first(), 2, "parser.py:30, test_names passes")
        story.agent_clocks_out(story.agents.workers.first(), "the parser is done")

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.DELIVERED)
        story.expect_agent_told(story.agents.main, WorkersNudges.WORK_READY)
        story.expect_stack(story.agents.workers.first(), Void)

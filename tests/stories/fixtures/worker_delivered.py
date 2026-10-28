from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.task_with_points_open import TaskWithPointsOpen


class WorkerDelivered(StateFixture):
    """A worker sent on the open task clocked in, proved both points and clocked out, its work waiting for the agent's check: start.worker."""

    stack = (Ready,)

    builds_on = TaskWithPointsOpen

    def steps(self, story) -> None:
        self.worker = story.agent_dispatches_worker("Lady Lovelace", self.open_task)
        story.worker_clocks_in(self.worker)
        story.worker_proves(self.worker, 1, "parser.py:12, test_reads passes")
        story.worker_proves(self.worker, 2, "parser.py:30, test_names passes")
        story.worker_clocks_out(self.worker, "the parser is done")

    def expected(self, story) -> None:
        story.expect_worker(self.worker, state=WorkerState.DELIVERED)
        story.expect_agent_told(WorkersNudges.WORK_READY)

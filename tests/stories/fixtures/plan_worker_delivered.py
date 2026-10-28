from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.plan_worker import PlanWorker
from tests.stories.fixtures.state_fixture import StateFixture


class PlanWorkerDelivered(StateFixture):
    """The worker on the whole plan proved and clocked out of both its tasks, one after the other, and its work waits for the agent's check."""

    stack = (Ready,)

    parent = PlanWorker

    def steps(self, story) -> None:
        story.worker_proves(self.worker, 1, "first.py:3, test_first passes")
        story.worker_clocks_out(self.worker, "the first is done")
        story.worker_proves(self.worker, 1, "second.py:3, test_second passes")
        story.worker_clocks_out(self.worker, "the plan is done")

    def expected(self, story) -> None:
        story.expect_worker(self.worker, state=WorkerState.DELIVERED)
        story.expect_agent_told(WorkersNudges.WORK_READY)

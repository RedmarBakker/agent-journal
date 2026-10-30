from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.worker.plan_worker import PlanWorker
from tests.stories.fixtures.state_fixture import StateFixture


class PlanWorkerDelivered(StateFixture):
    """The worker on the whole plan proved both its tasks, the second handed to it as the first was proved, and clocked out once, and its work waits for the agent's check."""

    stack = (Ready,)

    parent = PlanWorker

    def steps(self, story) -> None:
        story.agent_proves(story.agents.workers.first(), 1, "first.py:3, test_first passes")
        story.agent_proves(story.agents.workers.first(), 1, "second.py:3, test_second passes")
        story.agent_clocks_out(story.agents.workers.first(), "the plan is done")

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.DELIVERED)
        story.last_step.expect_agent_told(story.agents.main, WorkersNudges.WORK_READY)

from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.state_fixture import StateFixture


class DependencyPlanWorker(StateFixture):
    """The plan's prerequisite is assigned to a worker; its dependent task stays open in the plan."""

    stack = (Ready, ExternalWait)
    parent = PlanApproved

    def steps(self, story) -> None:
        story.user_presses(f"/journal/plans/{self.plans.first}/dependencies", {
            "task_id": self.tasks.second, "prerequisites": [self.tasks.first], "reason": "the second task uses the first task output",
        }).expect_viewer_passed()
        self.workers.first = story.agent_dispatches_worker_on_plan(story.agents.main, "Lady Lovelace", self.plans.first)
        worker = story.agents.workers.get(self.workers.first)
        story.agent_starts_a_session(worker)
        story.agent_clocks_in(worker)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DELEGATED)
        story.expect_task(self.tasks.first, state=TaskState.STARTED, delegated=True)
        story.expect_task(self.tasks.second, state=TaskState.OPEN, delegated=False)
        story.expect_worker(self.workers.first, state=WorkerState.READY)

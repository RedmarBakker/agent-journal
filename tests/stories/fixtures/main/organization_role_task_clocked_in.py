from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.organization_role_worker_started import OrganizationRoleWorkerStarted


class OrganizationRoleTaskClockedIn(OrganizationRoleWorkerStarted):
    """The Domain handed its task to a writing Role, whose seat started and clocked in."""

    parent = OrganizationRoleWorkerStarted

    def steps(self, story) -> None:
        worker = story.agents.workers.first()
        story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED)
        story.expect_task(self.tasks.second, state=TaskState.STARTED, delegated=True)
        worker = story.agents.workers.first()
        story.expect_worker_role_job(worker, self.tasks.second, "- task 6 has its current brief", "- first is done")
        story.expect_worker(worker, state=WorkerState.READY)
        story.expect_stack(worker, Void, WorkingTask)

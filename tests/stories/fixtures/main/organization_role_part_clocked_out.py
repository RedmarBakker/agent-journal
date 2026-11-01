from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.organization_task_part_clocked_in import OrganizationTaskPartClockedIn


class OrganizationRolePartClockedOut(OrganizationTaskPartClockedIn):
    """A Role worker has clocked out of its split part while its plan still runs."""

    parent = OrganizationTaskPartClockedIn
    settings = ()

    def steps(self, story) -> None:
        worker = story.agents.workers.first()
        story.agent_runs_from_openrig_organization_seat(
            worker, "role:alpha/builder", "proof 1 'the assigned part is complete'",
        ).expect_command_passed()
        story.agent_runs_from_openrig_organization_seat(
            worker, "role:alpha/builder", "clock-out 'the assigned part is complete'",
        ).expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first_part, state=TaskState.STARTED, delegated=True)
        story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)

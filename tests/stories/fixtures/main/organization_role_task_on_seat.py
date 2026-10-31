from journal.engine.states.void import Void
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.states.working_task import WorkingTask
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.organization_domain_role_task import OrganizationDomainRoleTask


class OrganizationRoleTaskOnSeat(OrganizationDomainRoleTask):
    """A Role worker has clocked in on the handed-off plan task."""

    parent = OrganizationDomainRoleTask

    def steps(self, story) -> None:
        task = self.tasks.second
        story.agent_runs_from_organization_seat(
            story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
        ).expect_command_passed()
        self.workers.first = story.newest("workers")
        worker = story.agents.workers.first()
        story.agent_starts_role_session(worker).expect_allowed(worker)
        story.expect_worker_role_job(worker, task, "- task 6 has its current brief", "the earlier task brief")
        story.expect_role_job_prompt(worker, "- task 6 has its current brief", "the earlier task brief", "journal clock-in")
        story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED)
        story.expect_task(self.tasks.second, state=TaskState.STARTED, delegated=True)
        story.expect_worker_role_job(story.agents.workers.first(), self.tasks.second, "- task 6 has its current brief", "- first is done")
        story.expect_worker(self.workers.first, state=WorkerState.READY)
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)

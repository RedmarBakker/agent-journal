from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.organization_role_task_on_seat import OrganizationRoleTaskOnSeat
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


class OrganizationRoleWorkerEnded(OrganizationRoleTaskOnSeat):
    """A clocked-in Role worker ends without clocking out while holding its plan task."""

    parent = OrganizationRoleTaskOnSeat

    def steps(self, story) -> None:
        worker = story.agents.workers.first()
        story.expect_worker_role_job(worker, self.tasks.second, "- task 6 has its current brief", "the earlier task brief")
        story.expect_role_job_prompt(worker, "- task 6 has its current brief", "the earlier task brief", "journal clock-in")
        story.worker_run_ends_without_clocking_out(worker)

    def expected(self, story) -> None:
        story.expect_task(self.tasks.second, delegated=True)
        story.expect_worker(self.workers.first, state=WorkerState.UNFINISHED)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan, awaiting_state(story))

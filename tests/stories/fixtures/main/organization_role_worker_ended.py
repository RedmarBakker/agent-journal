from journal.models.worker_state import WorkerState
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from tests.stories.fixtures.main.organization_role_worker_started import OrganizationRoleWorkerStarted
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


class OrganizationRoleWorkerEnded(OrganizationRoleWorkerStarted):
    """A writing Role's worker ended without clocking out while holding its plan task."""

    parent = OrganizationRoleWorkerStarted

    def steps(self, story) -> None:
        task = self.tasks.second
        worker = story.agents.workers.first()
        story.expect_worker_role_job(worker, task, "- task 6 has its current brief", "the earlier task brief")
        story.expect_role_job_prompt(worker, "- task 6 has its current brief", "the earlier task brief", "journal clock-in")
        story.agent_clocks_in(worker).expect_command_passed()
        story.worker_run_ends_without_clocking_out(worker)

    def expected(self, story) -> None:
        story.expect_task(self.tasks.second, delegated=True)
        story.expect_worker(self.workers.first, state=WorkerState.UNFINISHED)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan, awaiting_state(story))

from journal.models.worker_state import WorkerState
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from tests.stories.fixtures.main.organization_domain_role_task import OrganizationDomainRoleTask
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


class OrganizationRoleWorkerEnded(OrganizationDomainRoleTask):
    """A writing Role's worker ended without clocking out while holding its plan task."""

    parent = OrganizationDomainRoleTask

    def steps(self, story) -> None:
        task = self.tasks.second
        result = story.agent_runs_from_organization_seat(
            story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
        )
        result.expect_command_passed()
        self.workers.first = story.newest("workers")
        worker = story.agents.workers.first()
        story.agent_starts_role_session(worker)
        story.expect_worker_role_job(worker, task, "- task 6 has its current brief", "the earlier task brief")
        story.expect_role_job_prompt(worker, "- task 6 has its current brief", "the earlier task brief", "journal clock-in")
        story.worker_run_ends_with_its_session(worker, "the Role ended before clocking in")

    def expected(self, story) -> None:
        story.expect_task(self.tasks.second, delegated=True)
        story.expect_worker(self.workers.first, state=WorkerState.UNFINISHED)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan, awaiting_state(story))

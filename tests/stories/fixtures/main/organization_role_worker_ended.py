from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.organization_domain_role_task import OrganizationDomainRoleTask


class OrganizationRoleWorkerEnded(OrganizationDomainRoleTask):
    """A writing Role's worker ended without clocking out while holding its plan task."""

    parent = OrganizationDomainRoleTask

    def steps(self, story) -> None:
        super().steps(story)
        task = self.tasks.second
        result = story.agent_runs_from_organization_seat(
            story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
        )
        result.expect_command_passed()
        self.workers.first = story.newest("workers")
        worker = story.agents.workers.first()
        story.agent_starts_role_session(worker)
        story.worker_run_ends_with_its_session(worker, "the Role ended before clocking in")

    def expected(self, story) -> None:
        super().expected(story)
        story.expect_task(self.tasks.second, delegated=True)
        story.expect_worker(self.workers.first, state=WorkerState.UNFINISHED)

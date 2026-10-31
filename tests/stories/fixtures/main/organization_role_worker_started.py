from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_domain_role_task import OrganizationDomainRoleTask
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


class OrganizationRoleWorkerStarted(OrganizationDomainRoleTask):
    """A Domain handed its task to a writing Role and its worker started a session."""

    parent = OrganizationDomainRoleTask
    settings = ()

    def steps(self, story) -> None:
        task = self.tasks.second
        handed = story.agent_runs_from_organization_seat(
            story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
        )
        handed.expect_command_passed()
        self.workers.first = story.newest("workers")
        worker = story.agents.workers.first()
        story.agent_starts_role_session(worker).expect_allowed(worker)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED)
        story.expect_task(self.tasks.second, state=TaskState.OPEN, delegated=True)
        story.expect_worker_role_job(
            story.agents.workers.first(), self.tasks.second, "- task 6 has its current brief", "- first is done",
        )
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan, awaiting_state(story))

from journal.engine.states.void import Void
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.workers.states.working_task import WorkingTask
from journal.repositories.plans import Plans
from tests.stories.fixtures.main.organization_plan_without_domain_seats import TASK_BRIEF
from tests.stories.fixtures.main.organization_shared_role_git_project import OrganizationSharedRoleGitProject


class OrganizationSharedRoleTaskClockedIn(OrganizationSharedRoleGitProject):
    """A journal-cardinality Role seat is clocked in on a task in a clean target checkout."""

    parent = OrganizationSharedRoleGitProject

    def steps(self, story) -> None:
        plan, task = story.plans.first, story.tasks.first
        domain = story.organization_seat_agent("domain:alpha")
        handed = story.agent_runs_from_openrig_organization_seat(
            domain, "domain:alpha", f"organization handoff {task} role:alpha/shared",
        )
        handed.expect_command_passed()

        self.workers.first = story.newest("workers")
        worker = story.agents.workers.first()
        story.expect_worker_role_job(worker, task, TASK_BRIEF, "the earlier task brief")
        started = story.agent_starts_role_session(worker)
        started.expect_allowed(worker)
        plan_row = story.app.container.get(Plans).global_matching(id=plan)[0]
        shared_rig = story.app.container.get(RigStaffing).shared_rig_name(plan_row.environment_id)
        story.expect_openrig_seat_environment(
            worker, "role:alpha/shared", shared_rig,
        )
        story.agent_clocks_in(worker).expect_command_passed()

    def expected(self, story) -> None:
        worker = story.agents.workers.first()
        story.expect_worker(worker, worktree=False)
        story.expect_stack(worker, Void, WorkingTask)

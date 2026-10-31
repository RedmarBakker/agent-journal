from journal.engine.states.void import Void
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.states.working_task import WorkingTask
from tests.stories.fixtures.main.organization_domain_seat_started import OrganizationDomainSeatStarted
from tests.stories.fixtures.main.organization_plan_without_domain_seats import TASK_BRIEF

STALE_BRIEF = "the earlier task brief"


class OrganizationRoleWorkerClockedIn(OrganizationDomainSeatStarted):
    """An organization Domain has handed its task to a clocked-in Role worker."""

    parent = OrganizationDomainSeatStarted

    def steps(self, story) -> None:
        plan, task = story.plans.first, story.tasks.first
        domain = story.organization_seat_agent("domain:alpha")
        inbox = story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox")
        inbox.expect_command_passed()
        inbox.expect_command_text(f"plan {plan} task {task}: first")
        inbox.expect_command_text(TASK_BRIEF)
        handed_to_role = story.agent_runs_from_openrig_organization_seat(
            domain, "domain:alpha", f"organization handoff {task} role:alpha/builder",
        )
        handed_to_role.expect_command_passed()
        self.workers.first = story.newest("workers")
        role = story.agents.workers.first()
        role_started = story.agent_starts_role_session(role)
        role_started.expect_allowed(role)
        story.expect_openrig_seat_environment(role, "role:alpha/builder")
        story.expect_role_job_prompt(role, TASK_BRIEF, STALE_BRIEF, "journal clock-in")
        inbox = story.agent_runs_from_openrig_organization_seat(role, "role:alpha/builder", "organization inbox")
        inbox.expect_command_passed()
        inbox.expect_command_text(TASK_BRIEF)
        clocked_in = story.agent_runs_from_openrig_organization_seat(role, "role:alpha/builder", "clock-in")
        clocked_in.expect_command_passed()

    def expected(self, story) -> None:
        story.expect_task(story.tasks.first, delegated=True)
        story.expect_organization_seat_routing_guidance(story.plan_rig_name(story.plans.first))
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)

from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats
from tests.stories.fixtures.main.paused_organization_plan_task import PausedOrganizationPlanTask


class PausedOrganizationPlanRoleRoute(PausedOrganizationPlanTask):
    """A paused organization plan has a read Domain handoff and all its plan seats."""

    parent = PausedOrganizationPlanTask

    def steps(self, story) -> None:
        plan, task = self.plans.first, self.tasks.first
        story.plays_in(BUILDER_MODE)
        story.user_starts_plan(plan).expect_viewer_passed()
        runtime = story.app.container.get(SeatRuntime)
        OrganizationPlanWithDomainSeats.add_domain_seats(self, story, runtime)

        plan_seat = story.organization_seat_agent("plan")
        plan_started = story.agent_starts_plan_seat(plan_seat, plan)
        plan_started.expect_agent_told(
            plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha",
        )
        handoff = story.agent_runs_as_organization_seat(
            plan_seat, "plan", f"organization handoff {task} domain:alpha",
        )
        handoff.expect_command_passed()
        domain = story.organization_seat_agent("domain:alpha")
        self.domain_agent = domain
        domain_started = story.agent_starts_organization_seat(domain, "domain:alpha")
        domain_started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
        inbox = story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox")
        inbox.expect_command_passed()
        story.user_pauses_plan(plan).expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, delegated=False)
        story.expect_task_unheld(self.tasks.first)
        story.expect_task(self.tasks.second, state=TaskState.PAUSED, delegated=False)
        story.expect_stack(self.domain_agent, LeadingPlan, FollowingPlan)

from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats
from tests.stories.fixtures.main.started_organization_plan_task import StartedOrganizationPlanTask


class PausedOrganizationPlanRoleRoute(StartedOrganizationPlanTask):
    """A paused organization plan has a read Domain handoff and all its plan seats."""

    parent = StartedOrganizationPlanTask

    def steps(self, story) -> None:
        runtime = story.app.container.get(SeatRuntime)
        OrganizationPlanWithDomainSeats.add_domain_seats(self, story, runtime)
        story.observed("OpenRig refreshes the plan rig with all Domain seats", None, None)
        plan, task = self.plans.first, self.tasks.first
        plan_seat = story.organization_seat_agent("plan")
        plan_started = story.agent_starts_plan_seat(plan_seat, plan)
        plan_started.expect_agent_told(
            plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha",
        )
        story.agent_runs_as_organization_seat(
            plan_seat, "plan", f"organization handoff {task} domain:alpha",
        ).expect_command_passed()
        self.domain_agent = story.organization_seat_agent("domain:alpha")
        domain_started = story.agent_starts_organization_seat(self.domain_agent, "domain:alpha")
        domain_started.expect_agent_told(self.domain_agent, OrganizationNudges.UNREAD_HANDOFF)
        story.agent_runs_as_organization_seat(
            self.domain_agent, "domain:alpha", "organization inbox",
        ).expect_command_passed()
        story.user_pauses_plan(plan).expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, delegated=False)
        story.expect_task_unheld(self.tasks.first)
        story.expect_task(self.tasks.second, state=TaskState.BLOCKED, delegated=False)
        story.expect_stack(self.domain_agent, LeadingPlan, FollowingPlan)

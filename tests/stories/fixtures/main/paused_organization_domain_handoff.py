from journal.features.organization.organization_nudges import OrganizationNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_organization_plan_task import StartedOrganizationPlanTask


class PausedOrganizationDomainHandoff(StartedOrganizationPlanTask):
    """A paused organization plan has a read handoff to its Domain seat."""

    parent = StartedOrganizationPlanTask

    def steps(self, story) -> None:
        plan, task = self.plans.first, self.tasks.first
        plan_seat = story.organization_seat_agent("plan")
        started = story.agent_starts_plan_seat(plan_seat, plan)
        started.expect_agent_told(plan_seat, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                  task=task, domain="alpha")
        story.agent_runs_from_plan_organization_seat(
            plan_seat, "plan", f"organization handoff {task} domain:alpha",
        ).expect_command_passed()

        domain = story.organization_seat_agent("domain:alpha")
        domain_started = story.agent_starts_organization_seat(domain, "domain:alpha")
        domain_started.expect_agent_told(domain, OrganizationNudges.UNREAD_HANDOFF)
        story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox").expect_command_passed()
        story.user_pauses_plan(plan).expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, delegated=False)
        story.expect_task_unheld(self.tasks.first)
        story.expect_task(self.tasks.second, state=TaskState.BLOCKED, delegated=False)

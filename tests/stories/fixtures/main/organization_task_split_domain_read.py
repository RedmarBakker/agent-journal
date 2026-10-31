from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_task_split_plan import OrganizationTaskSplitPlan


class OrganizationTaskSplitDomainRead(OrganizationTaskSplitPlan):
    """The Alpha Domain seat has read its plan task handoff."""

    parent = OrganizationTaskSplitPlan

    def steps(self, story) -> None:
        plan, task = story.plans.first, story.tasks.first
        handed = story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"organization handoff {task} domain:alpha",
        )
        handed.expect_command_passed()
        domain = story.organization_seat_agent("domain:alpha")
        story.expect_openrig_seat_received(domain, f"plan-{plan}", "domain:alpha", OrganizationSeatRouting.handoff_prompt)
        started = story.agent_starts_organization_seat(domain, "domain:alpha")
        started.expect_allowed(domain)
        started.expect_agent_told(domain, OrganizationNudges.TASK_CAN_BE_SPLIT, task=task, domain="alpha")
        story.agent_runs_as_organization_seat(domain, "domain:alpha", "organization inbox").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)

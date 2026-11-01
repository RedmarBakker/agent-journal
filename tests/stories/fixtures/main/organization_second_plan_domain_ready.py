from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_role_part_clocked_out import OrganizationRolePartClockedOut


def second_plan_with_domain_ready(story):
    plan = story.user_creates_plan("Second plan", "Finish the second organization plan")
    task = story.user_adds_plan_task(plan, "second parent", "alpha")
    story.agent_runs(story.agents.subject, f"plan mode {plan} organization").expect_command_passed()
    story.user_approves_plan(plan).expect_viewer_passed()
    story.user_starts_plan(plan).expect_viewer_passed()
    plan_seat = story.organization_seat_agent_in_plan("plan", plan)
    story.agent_starts_organization_seat_in_plan(plan_seat, "plan", plan).expect_allowed(plan_seat)
    story.agent_runs_as_organization_seat_in_plan(
        plan_seat, "plan", plan, f"organization handoff {task} domain:alpha",
    ).expect_command_passed()
    domain = story.organization_seat_agent_in_plan("domain:alpha", plan)
    story.agent_starts_organization_seat_in_plan(domain, "domain:alpha", plan).expect_allowed(domain)
    story.agent_runs_as_organization_seat_in_plan(domain, "domain:alpha", plan, "organization inbox").expect_command_passed()
    return plan, task


class OrganizationSecondPlanDomainReady(OrganizationRolePartClockedOut):
    """A second plan has an active Domain seat while the first plan's Role waits to merge."""

    parent = OrganizationRolePartClockedOut
    settings = ()

    def steps(self, story) -> None:
        self.plans.second, self.tasks.second = second_plan_with_domain_ready(story)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_plan(self.plans.second, state=PlanState.STARTED)
        story.expect_task(self.tasks.second, state=TaskState.OPEN)
        domain = story.organization_seat_agent_in_plan("domain:alpha", self.plans.second)
        story.expect_stack(domain, LeadingPlan, FollowingPlan)

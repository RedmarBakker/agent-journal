from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.organization_domain_plan_draft import OrganizationDomainPlanDraft


class OrganizationPlanSeat(OrganizationDomainPlanDraft):
    """An approved organization plan has a planned Alpha task and a simulated OpenRig."""

    parent = OrganizationDomainPlanDraft
    settings = ()

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first).expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.APPROVED)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.agents.main, CoordinatingPlans)

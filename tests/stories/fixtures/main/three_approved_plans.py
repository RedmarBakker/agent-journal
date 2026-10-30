from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class ThreeApprovedPlans(StateFixture):
    """Beside the plan the user drafted, the user made billing with two tasks, the first of them the invoice, and docs with one, and approved all three, none started: story.plans.first, story.plans.second, story.tasks.invoice and story.plans.third."""

    stack = (Ready,)

    parent = UserDraftedPlan

    def steps(self, story) -> None:
        self.plans.second = story.user_creates_plan("billing", "ship billing")
        self.tasks.invoice = story.user_adds_plan_task(self.plans.second, "the invoice")
        story.user_adds_plan_task(self.plans.second, "the receipt")
        self.plans.third = story.user_creates_plan("docs", "ship the docs")
        story.user_adds_plan_task(self.plans.third, "the page")
        for plan in (self.plans.first, self.plans.second, self.plans.third):
            story.user_approves_plan(plan)

    def expected(self, story) -> None:
        for plan in (self.plans.first, self.plans.second, self.plans.third):
            story.expect_plan(plan, state=PlanState.APPROVED)

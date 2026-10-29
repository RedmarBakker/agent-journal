from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class UserDraftedPlan(StateFixture):
    """The user made a plan in the viewer with two tasks, each with a brief a worker can prove, not yet approved: story.plans.first, story.tasks.first and story.tasks.second."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.plans.first = story.user_creates_plan("p", "b")
        self.tasks.first = story.user_adds_plan_task(self.plans.first, "first")
        self.tasks.second = story.user_adds_plan_task(self.plans.first, "second")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)

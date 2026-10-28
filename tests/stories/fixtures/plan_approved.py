from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class PlanApproved(StateFixture):
    """The user made a plan with two tasks, each with a brief a worker can prove, and approved it in the viewer, not yet started: start.plan, start.first_task and start.second_task."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.plan = story.user_creates_plan("p", "b")
        self.first_task = story.user_adds_plan_task(self.plan, "first")
        self.second_task = story.user_adds_plan_task(self.plan, "second")
        story.user_approves_plan(self.plan)

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.APPROVED)

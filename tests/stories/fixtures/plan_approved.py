from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.agent_at_work import AgentAtWork
from tests.stories.fixtures.state_fixture import StateFixture


class PlanApproved(StateFixture):
    """The user made a plan with two tasks, each with a brief a worker can prove, and approved it in the viewer, not yet started: start.plan."""

    stack = (Ready,)

    builds_on = AgentAtWork

    def steps(self, story) -> None:
        self.plan = story.user_creates_plan("p", "b")
        story.user_adds_plan_task(self.plan, "first", "- writes part one")
        story.user_adds_plan_task(self.plan, "second", "- writes part two")
        story.user_approves_plan(self.plan)

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.APPROVED)

from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.paused_plan_outside_task import PausedPlanOutsideTask
from tests.stories.fixtures.state_fixture import StateFixture


class PlanReturn(StateFixture):
    """The agent said yes, it returns to the plan it paused: the plan is started again under the outside task, which stays in hand."""

    stack = (Ready, FollowingPlan, Working)

    parent = PausedPlanOutsideTask

    def steps(self, story) -> None:
        story.agent_runs(f"plan return {self.plan} yes")

    def expected(self, story) -> None:
        story.expect_command_passed()
        story.expect_plan(self.plan, state=PlanState.STARTED)
        story.expect_task(self.fix, state=TaskState.STARTED)
        story.expect_stack(Ready, FollowingPlan, Working)

from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class StartedTwoTaskPlan(StateFixture):
    """The user made a plan with two tasks and approved it in the viewer, and the agent at work started it: start.plan, its first task in hand as start.started_task and the next as start.next_task."""

    stack = (Ready, FollowingPlan)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.plan = story.user_creates_plan("p", "b")
        self.started_task = story.user_adds_plan_task(self.plan, "first")
        self.next_task = story.user_adds_plan_task(self.plan, "second")
        story.user_approves_plan(self.plan)
        story.agent_runs(f"plan start {self.plan}")

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.STARTED)
        story.expect_task(self.started_task, state=TaskState.STARTED)

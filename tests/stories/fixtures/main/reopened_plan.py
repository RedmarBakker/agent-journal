from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class ReopenedPlan(StateFixture):
    """The plan was blocked by its second task and reopened when that task was unblocked."""

    stack = (Ready, FollowingPlan)

    parent = StartedPlan

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"task block {self.tasks.second} 'waits on the designer'")
        story.agent_runs(story.agents.main, f"task complete {self.tasks.first} --how done")
        result = story.agent_runs(story.agents.main, f"task unblock {self.tasks.second}")
        result.expect_agent_told(story.agents.main, PlansNudges.PLAN_REOPENED, n=self.plans.first)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED)
        story.expect_task(self.tasks.second, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, Ready, FollowingPlan)

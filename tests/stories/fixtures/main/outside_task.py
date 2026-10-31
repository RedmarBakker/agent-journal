from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class OutsideTask(StateFixture):
    """The agent took up a task outside the plan over the plan's first task, which is blocked until it closes, worked on top of the plan: story.tasks.outside, with story.plans.first, story.tasks.first and story.tasks.second."""

    stack = (Ready, FollowingPlan, Working)

    parent = StartedPlan

    def steps(self, story) -> None:
        self.tasks.outside = story.agent_takes_a_task(story.agents.main, "outside")

    def expected(self, story) -> None:
        story.expect_task(self.tasks.outside, state=TaskState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.BLOCKED)
        story.expect_stack(story.agents.main, Ready, FollowingPlan, Working)

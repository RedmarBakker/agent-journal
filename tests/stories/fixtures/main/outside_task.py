from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class OutsideTask(StateFixture):
    """The agent paused the plan's first task and took up a task outside the plan, worked on top of the plan: start.outside_task, with start.plan, start.first_task and start.second_task."""

    stack = (Ready, FollowingPlan, Working)

    parent = StartedPlan

    def steps(self, story) -> None:
        story.agent_runs(story.agents.subject, f"task pause {self.first_task} 'something else first'")
        self.outside_task = story.agent_takes_a_task(story.agents.subject, "outside")

    def expected(self, story) -> None:
        story.expect_task(self.outside_task, state=TaskState.STARTED)
        story.expect_task(self.first_task, state=TaskState.PAUSED)
        story.expect_stack(story.agents.subject, Ready, FollowingPlan, Working)

from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PausedPlan(StateFixture):
    """The user paused the started plan in the viewer, which pauses its task in hand and frees the agent: start.plan, start.first_task and start.second_task."""

    stack = (Ready,)

    parent = StartedPlan

    def steps(self, story) -> None:
        story.user_pauses_plan(self.plan)

    def expected(self, story) -> None:
        story.expect_agent_told(PlansNudges.PLAN_POSTPONED, n=self.plan)
        story.expect_plan(self.plan, state=PlanState.PAUSED)
        story.expect_task(self.first_task, state=TaskState.PAUSED)

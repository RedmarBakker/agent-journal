from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PausedPlan(StateFixture):
    """The user paused the started plan in the viewer, which sets its task in hand aside, open again, and frees the agent: story.plans.first, story.tasks.first and story.tasks.second."""

    stack = (Ready,)

    parent = StartedPlan

    def steps(self, story) -> None:
        story.user_pauses_plan(self.plans.first)

    def expected(self, story) -> None:
        story.last_step.expect_agent_told(story.agents.main, PlansNudges.PLAN_POSTPONED, n=self.plans.first)
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)

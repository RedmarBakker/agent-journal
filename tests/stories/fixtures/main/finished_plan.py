from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class FinishedPlan(StateFixture):
    """The agent completed both tasks of the plan, so the plan is done: start.plan, start.first_task and start.second_task."""

    stack = (Ready,)

    parent = StartedPlan

    def steps(self, story) -> None:
        story.agent_runs(f"task complete {self.first_task} --how done")
        story.agent_runs(f"task complete {self.second_task} --how done")

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.FINISHED)
        story.expect_stack(Ready)

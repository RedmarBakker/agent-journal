from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class AgentPausedPlan(StateFixture):
    """The agent following the plan paused it itself, to do something outside it first."""

    stack = (Ready,)

    parent = StartedPlan

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan pause {self.plans.first}")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_stack(story.agents.main, Ready)

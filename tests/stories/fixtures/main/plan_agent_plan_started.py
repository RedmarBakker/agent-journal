from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.coordinating_plan_agent import CoordinatingPlanAgent
from tests.stories.fixtures.state_fixture import StateFixture


class PlanAgentPlanStarted(StateFixture):
    """The owner started an approved plan with its Plan agent prepared to launch."""

    parent = CoordinatingPlanAgent
    stack = (CoordinatingPlans, FollowingPlan)

    def steps(self, story) -> None:
        story.monkeypatch.setattr(AgentEnvironments, "launched", lambda places, environment, agent, repositories=None: None)
        result = story.agent_runs(story.agents.main, f"plan start {self.plans.first}")
        result.expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_task_unheld(self.tasks.first)
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)

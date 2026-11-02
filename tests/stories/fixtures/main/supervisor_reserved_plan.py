from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.coordinating_plan_agent import CoordinatingPlanAgent
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION
from tests.stories.fixtures.state_fixture import StateFixture


class SupervisorReservedPlan(StateFixture):
    """A live Plan agent has one open task the owner reserved for supervisor diagnosis."""

    parent = CoordinatingPlanAgent
    stack = (CoordinatingPlans, FollowingPlan)

    def steps(self, story) -> None:
        story.user_cancels_task(self.tasks.second, "the smoke uses one seed task").expect_viewer_passed()
        story.user_did(f"/journal/tasks/{self.tasks.first}", {"supervisor_reserved": True}, "the owner reserves the seed for supervisor diagnosis").expect_viewer_passed()
        story.monkeypatch.setattr(AgentEnvironments, "launched", lambda places, environment, agent, repositories=None: None)
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}").expect_command_passed()
        story.session_starts_in(f"plan-{self.plans.first}", PLAN_AGENT_SESSION).expect_allowed()
        story.agent_in_runs(story.agents.main, f"plan-{self.plans.first}", PLAN_AGENT_SESSION, "environment overview").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_task(self.tasks.first, state=TaskState.OPEN, supervisor_reserved=True)
        story.expect_task_unheld(self.tasks.first)
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)

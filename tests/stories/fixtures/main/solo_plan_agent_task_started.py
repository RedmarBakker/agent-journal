from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION, SoloPlanAgentStarted


class SoloPlanAgentTaskStarted(SoloPlanAgentStarted):
    """The Plan agent started its first plan task."""

    parent = SoloPlanAgentStarted

    def steps(self, story) -> None:
        agent = StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION)
        result = story.agent_in_runs(agent, f"plan-{self.plans.first}", PLAN_AGENT_SESSION, f"task start {self.tasks.first}")
        result.expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.STARTED)
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)

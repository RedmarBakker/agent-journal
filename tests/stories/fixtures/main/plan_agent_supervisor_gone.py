from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.solo_plan_agent_started import PLAN_AGENT_SESSION, SoloPlanAgentStarted
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.builder.story_agent import StoryAgent
from journal.support.agent_role import AgentRole


class PlanAgentSupervisorGone(StateFixture):
    """A started plan has a Plan agent whose supervisor stopped without closing its inbox."""

    parent = SoloPlanAgentStarted
    stack = (CoordinatingPlans, FollowingPlan)

    def steps(self, story) -> None:
        story.the_plan_agent_supervisor_stopped_without_closing_its_inbox(
            StoryAgent(AgentRole.MAIN, session=PLAN_AGENT_SESSION),
        )

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_stack(story.agents.main, CoordinatingPlans, FollowingPlan)

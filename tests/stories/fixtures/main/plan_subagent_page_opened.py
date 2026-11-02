from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.subagent_state import SubagentState
from tests.stories.fixtures.main.plan_subagent import PlanSubagent
from tests.stories.fixtures.state_fixture import StateFixture


class PlanSubagentPageOpened(StateFixture):
    """The plan's active background subagent is shown on its viewer page."""

    parent = PlanSubagent
    stack = (Ready, FollowingPlan)

    def steps(self, story) -> None:
        story.user_opens("/journal/subagents").expect_viewer_rows("rows", "state", [SubagentState.ACTIVE])

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready, FollowingPlan)

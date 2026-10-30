from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER

SUBAGENT = "plan-review"


class PlanSubagent(StateFixture):
    """The agent holds the started plan's first task while a background subagent reviews it."""

    stack = (Ready, FollowingPlan)
    parent = StartedPlan

    def steps(self, story) -> None:
        story.agent_sends_subagent_in_the_background(story.agents.main, RESEARCHER, "review the parser", SUBAGENT)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready, FollowingPlan)

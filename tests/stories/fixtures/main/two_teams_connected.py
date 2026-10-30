from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture

FIRST, SECOND = "shop", "studio"


class TwoTeamsConnected(StateFixture):
    """The user connected this journal to two teams through the viewer, shop first and studio second, as Ada, the admin of both."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.user_adds_a_team(FIRST)
        story.user_adds_a_team(SECOND)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)

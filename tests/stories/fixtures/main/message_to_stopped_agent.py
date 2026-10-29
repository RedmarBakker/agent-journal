from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class MessageToStoppedAgent(StateFixture):
    """The agent stopped, and the user's message to it typed the wake line into its terminal, not yet taken up: story.messages.first."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.agent_stops(story.agents.main)
        self.messages.first = story.user_sends_message("is the footer done?")

    def expected(self, story) -> None:
        story.expect_woken(1)
        story.expect_stack(story.agents.main, Ready)

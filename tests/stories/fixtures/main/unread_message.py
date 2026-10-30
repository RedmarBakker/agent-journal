from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class UnreadMessage(StateFixture):
    """The user asked whether the footer is done, and the agent has not read it yet: story.messages.first."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.messages.first = story.user_sends_message("is the footer done?")

    def expected(self, story) -> None:
        story.last_step.expect_agent_told(story.agents.main, MessagesNudges.NEW_MESSAGE, n=self.messages.first)

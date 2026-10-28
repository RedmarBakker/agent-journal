from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.working_agent import WorkingAgent


class TwoUnreadMessages(StateFixture):
    """The user sent two messages the agent has not read: start.first_message and start.second_message."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.first_message = story.user_sends_message("is the footer done?")
        self.second_message = story.user_sends_message("and the header?")

    def expected(self, story) -> None:
        story.expect_agent_told(MessagesNudges.NEW_MESSAGE, n=self.second_message)

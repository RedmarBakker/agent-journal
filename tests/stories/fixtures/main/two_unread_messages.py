from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.unread_message import UnreadMessage


class TwoUnreadMessages(StateFixture):
    """The user sent two messages the agent has not read: story.messages.first and story.messages.second."""

    stack = (Ready,)

    parent = UnreadMessage

    def steps(self, story) -> None:
        self.messages.second = story.user_sends_message("and the header?")

    def expected(self, story) -> None:
        story.last_step.expect_agent_told(story.agents.main, MessagesNudges.NEW_MESSAGE, n=self.messages.second)

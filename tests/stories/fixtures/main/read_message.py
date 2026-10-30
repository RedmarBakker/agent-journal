from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.unread_message import UnreadMessage


class ReadMessage(StateFixture):
    """The user asked whether the footer is done, and the agent read the message and has not answered yet: story.messages.first."""

    stack = (Ready,)

    parent = UnreadMessage

    def steps(self, story) -> None:
        story.agent_reads_message(story.agents.main, self.messages.first)

    def expected(self, story) -> None:
        story.last_step.expect_agent_told(story.agents.main, MessagesNudges.MESSAGE_READ, n=self.messages.first)
        story.last_step.expect_agent_told(story.agents.main, MessagesNudges.REPLY_COMMAND)

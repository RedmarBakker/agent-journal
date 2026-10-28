from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.working_agent import WorkingAgent


class ReadMessage(StateFixture):
    """The user asked whether the footer is done, and the agent read the message and has not answered yet: start.message."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.message = story.user_sends_message("is the footer done?")
        story.agent_reads_message(self.message)

    def expected(self, story) -> None:
        story.expect_agent_told(MessagesNudges.MESSAGE_READ, n=self.message)
        story.expect_agent_told(MessagesNudges.REPLY_COMMAND)

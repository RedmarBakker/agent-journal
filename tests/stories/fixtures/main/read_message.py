from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.working_agent import WorkingAgent


class ReadMessage(StateFixture):
    """The user asked whether the footer is done, and the agent read the message and has not answered yet: story.messages.first."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.messages.first = story.user_sends_message("is the footer done?")
        story.agent_reads_message(story.agents.main, self.messages.first)

    def expected(self, story) -> None:
        story.expect_agent_told(story.agents.main, MessagesNudges.MESSAGE_READ, n=self.messages.first)
        story.expect_agent_told(story.agents.main, MessagesNudges.REPLY_COMMAND)

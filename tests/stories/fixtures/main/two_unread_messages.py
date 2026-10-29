from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.working_agent import WorkingAgent


class TwoUnreadMessages(StateFixture):
    """The user sent two messages the agent has not read: story.messages.first and story.messages.second."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.messages.first = story.user_sends_message("is the footer done?")
        self.messages.second = story.user_sends_message("and the header?")

    def expected(self, story) -> None:
        story.expect_agent_told(story.agents.main, MessagesNudges.NEW_MESSAGE, n=self.messages.second)

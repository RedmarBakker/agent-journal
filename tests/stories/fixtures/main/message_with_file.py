from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.two_unread_messages import TwoUnreadMessages
from tests.stories.fixtures.state_fixture import StateFixture

FILE = "shot one.png"


class MessageWithFile(StateFixture):
    """The user attached a screenshot to the first of their two unread messages: story.messages.first."""

    stack = (Ready,)

    parent = TwoUnreadMessages

    def steps(self, story) -> None:
        story.user_attaches_file(self.messages.first, FILE, b"PNG")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)

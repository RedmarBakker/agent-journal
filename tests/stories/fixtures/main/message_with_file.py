from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture

FILE = "shot one.png"


class MessageWithFile(StateFixture):
    """The user sent a message about a screenshot and attached the picture to it, not yet read: start.message."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.message = story.user_sends_message("the screenshot of the bar")
        story.user_attaches_file(self.message, FILE, b"PNG")

    def expected(self, story) -> None:
        story.expect_stack(Ready)

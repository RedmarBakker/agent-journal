from journal.engine.states.demand_block import DemandBlock
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.state_fixture import StateFixture


class UnansweredMessage(StateFixture):
    """The user holds every tool from the first use after a read, so the agent's next tool after reading the message was refused until it answers: start.message."""

    stack = (Ready, DemandBlock)

    parent = ReadMessage

    settings = ((MessagesOptions.TOOL_BLOCK_LIMIT, 0),)

    def steps(self, story) -> None:
        story.agent_reads()

    def expected(self, story) -> None:
        story.expect_refused(MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=self.message)
        story.expect_stack(Ready, DemandBlock)

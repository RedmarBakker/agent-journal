from journal.engine.states.demand_block import DemandBlock
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.agent_at_work import AgentAtWork
from tests.stories.fixtures.state_fixture import StateFixture


class HeldForAnAnswer(StateFixture):
    """The user, holding every tool from the first use after a read, sent a message the agent read and left unanswered, so its next tool was refused: start.message."""

    stack = (Ready, DemandBlock)

    builds_on = AgentAtWork

    def steps(self, story) -> None:
        story.user_sets(MessagesOptions.TOOL_BLOCK_LIMIT, 0)
        self.message = story.user_sends_message("is the footer done?")
        story.agent_reads_message(self.message)
        story.agent_reads()

    def expected(self, story) -> None:
        story.expect_refused(MessagesNudges.UNANSWERED_TOOL_BLOCK, messages=self.message)
        story.expect_stack(Ready, DemandBlock)

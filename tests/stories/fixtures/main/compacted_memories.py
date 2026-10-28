from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.tasks.states.ready import Ready
from journal.models.memory import HEAVIEST, LOWEST_WEIGHT
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class CompactedMemories(StateFixture):
    """The agent kept a heavy and a light memory, and its context was compacted: the heavy one is a weight lighter, the light one has faded out, and the start lists the memories but names no takeover: start.heavy_memory, start.light_memory."""

    stack = (Ready, ReadingOverview)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.heavy_memory = story.agent_adds_memory("the footer links go in a list", HEAVIEST)
        self.light_memory = story.agent_adds_memory("the header waits on the logo", LOWEST_WEIGHT)
        story.context_is_compacted()

    def expected(self, story) -> None:
        story.expect_agent_told(BriefingNudges.ENVIRONMENT_MEMORIES)
        story.expect_agent_not_told(BriefingNudges.TAKEOVER)
        story.expect_row("memories", self.heavy_memory, {"weight": HEAVIEST - 1})
        story.expect_row_absent("memories", self.light_memory)

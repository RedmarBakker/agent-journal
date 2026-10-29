from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.tasks.states.ready import Ready
from journal.models.memory import HEAVIEST, LOWEST_WEIGHT
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class CompactedMemories(StateFixture):
    """The agent kept a heavy and a light memory, and its context was compacted: the heavy one is a weight lighter, the light one has faded out, and the start lists the memories but names no takeover: story.memories.heavy, story.memories.light."""

    stack = (Ready, ReadingOverview)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.memories.heavy = story.agent_adds_memory(story.agents.main, "the footer links go in a list", HEAVIEST)
        self.memories.light = story.agent_adds_memory(story.agents.main, "the header waits on the logo", LOWEST_WEIGHT)
        story.context_is_compacted()

    def expected(self, story) -> None:
        story.expect_agent_told(story.agents.main, BriefingNudges.ENVIRONMENT_MEMORIES)
        story.expect_agent_not_told(story.agents.main, BriefingNudges.TAKEOVER)
        story.expect_row("memories", self.memories.heavy, {"weight": HEAVIEST - 1})
        story.expect_row_absent("memories", self.memories.light)

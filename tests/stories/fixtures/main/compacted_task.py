from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.main.compacting_task import CompactingTask
from tests.stories.fixtures.state_fixture import StateFixture


class CompactedTask(StateFixture):
    """The compacting agent's session started again after the compaction, and the journal asks for the overview before anything else."""

    stack = (Ready, Working, ReadingOverview)

    parent = CompactingTask

    def steps(self, story) -> None:
        story.compacted_session_starts()

    def expected(self, story) -> None:
        story.expect_agent_told(BriefingNudges.OVERVIEW_FIRST)
        story.expect_stack(Ready, Working, ReadingOverview)

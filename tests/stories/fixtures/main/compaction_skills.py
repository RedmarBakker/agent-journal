from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.skills.feature import Skills
from journal.features.skills.skills_options import SkillsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.main.compacting_task import CompactingTask
from tests.stories.fixtures.state_fixture import StateFixture


class CompactionSkills(StateFixture):
    """The compacting agent's session started again with the compaction skills the journal ships owed, and the overview not run."""

    stack = (Ready, Working, ReadingOverview)

    parent = CompactingTask

    settings = ((SkillsOptions.COMPACTION_SKILLS, SkillsOptions.COMPACTION_SKILLS.default),)

    def steps(self, story) -> None:
        story.user_switches_on(Skills)
        story.compacted_session_starts()

    def expected(self, story) -> None:
        story.expect_agent_told(BriefingNudges.OVERVIEW_FIRST)

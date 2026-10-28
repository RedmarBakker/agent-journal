from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.main.compaction_skills import CompactionSkills
from tests.stories.fixtures.state_fixture import StateFixture

JOURNAL_SKILL, ETIQUETTE_SKILL = "journal", "journal-etiquette"


class CompactionSkillReads(StateFixture):
    """After the compaction the agent read both compaction skills, the overview still owed."""

    stack = (Ready, Working, ReadingOverview)

    parent = CompactionSkills

    def steps(self, story) -> None:
        story.agent_reads_a_skill(JOURNAL_SKILL)
        story.agent_reads_a_skill(ETIQUETTE_SKILL)

    def expected(self, story) -> None:
        story.expect_stack(Ready, Working, ReadingOverview)

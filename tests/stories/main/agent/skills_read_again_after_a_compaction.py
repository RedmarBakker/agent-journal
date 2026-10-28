from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.skills.skills_options import SkillsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.compacting_task import CompactingTask
from tests.stories.fixtures.main.compaction_skills import CompactionSkills
from tests.stories.fixtures.main.compaction_skill_reads import CompactionSkillReads

JOURNAL_SKILL, ETIQUETTE_SKILL = "journal", "journal-etiquette"


@story(CompactionSkills, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_write_after_a_compaction_is_told_every_skill_owed_and_the_overview(story):
    story.agent_writes("footer.py")
    story.expect_refused(BriefingNudges.SKILLS_AND_OVERVIEW_REQUEST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, ReadingOverview)


@story(CompactionSkills, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_overview_alone_leaves_the_skills_owed(story):
    story.agent_looks_at_the_overview()
    story.agent_writes("footer.py")
    story.expect_refused(SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(Ready, Working)


@story(CompactionSkillReads, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_skills_and_then_the_overview_free_every_tool(story):
    story.agent_looks_at_the_overview()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_stack(Ready, Working)


@story(CompactionSkillReads, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_with_the_skills_read_a_write_is_told_only_the_overview(story):
    story.agent_writes("footer.py")
    story.expect_refused(BriefingNudges.OVERVIEW_FIRST)
    story.expect_stack(Ready, Working, ReadingOverview)


@story(CompactingTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(SkillsOptions.COMPACTION_SKILLS, [])
def test_with_no_compaction_skills_set_a_write_is_told_only_the_overview(story):
    story.compacted_session_starts()
    story.agent_writes("footer.py")
    story.expect_refused(BriefingNudges.OVERVIEW_FIRST)
    story.expect_agent_not_told(SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(Ready, Working, ReadingOverview)

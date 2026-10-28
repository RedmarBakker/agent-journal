from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.skills.skills_options import SkillsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.session_opening import SessionOpening
from tests.stories.fixtures.main.working_agent import WorkingAgent

JOURNAL_SKILL, ETIQUETTE_SKILL = "journal", "journal-etiquette"


@story(SessionOpening, mode=BUILDER_MODE)
def test_a_new_session_reads_the_start_skills_before_it_may_read_anything_else(story):
    story.agent_reads("footer.py")
    story.expect_refused(SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(Ready)


@story(SessionOpening, mode=BUILDER_MODE)
def test_a_start_skill_may_be_read_before_the_others_are(story):
    story.agent_reads_a_skill(JOURNAL_SKILL)
    story.expect_allowed()
    story.agent_reads("footer.py")
    story.expect_refused(SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(Ready)


@story(SessionOpening, mode=BUILDER_MODE)
def test_once_every_start_skill_is_read_and_the_overview_run_the_tools_are_free(story):
    story.agent_reads_a_skill(JOURNAL_SKILL)
    story.agent_reads_a_skill(ETIQUETTE_SKILL)
    story.agent_looks_at_the_overview()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_agent_not_told(SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(Ready)


@story(SessionOpening, mode=BUILDER_MODE)
def test_a_stop_with_a_start_skill_unread_is_refused(story):
    story.agent_looks_at_the_overview()
    story.agent_stops()
    story.expect_refused(SkillsNudges.UNREAD_SKILL_STOP)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(SkillsOptions.START_SKILLS, [])
def test_with_no_start_skills_set_a_new_session_is_asked_for_none(story):
    story.agent_starts_a_session()
    story.expect_agent_not_told(SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(Ready)

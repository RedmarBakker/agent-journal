from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.skills.skills_options import SkillsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.session_opening import SessionOpening
from tests.stories.fixtures.main.working_agent import WorkingAgent

JOURNAL_SKILL, ETIQUETTE_SKILL, MESSAGES_SKILL = "journal", "journal-etiquette", "journal-messages"


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_session_reads_the_start_skills_before_it_may_read_anything_else(story):
    result = story.agent_reads(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    for name in ("journal", "etiquette", "messages"):
        result.expect_agent_told_words(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST, f"the {name} skill")
    story.expect_stack(story.agents.subject, Ready)


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_start_skill_may_be_read_before_the_others_are(story):
    result = story.agent_reads_a_skill(story.agents.subject, JOURNAL_SKILL)
    result.expect_allowed()
    result = story.agent_reads(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(story.agents.subject, Ready)


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_once_every_start_skill_is_read_and_the_overview_run_the_tools_are_free(story):
    story.agent_reads_a_skill(story.agents.subject, JOURNAL_SKILL)
    story.agent_reads_a_skill(story.agents.subject, ETIQUETTE_SKILL)
    story.agent_reads_a_skill(story.agents.subject, MESSAGES_SKILL)
    story.agent_looks_at_the_overview(story.agents.subject)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(story.agents.subject, Ready)


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_stop_with_a_start_skill_unread_is_refused(story):
    story.agent_looks_at_the_overview(story.agents.subject)
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, SkillsNudges.UNREAD_SKILL_STOP)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(SkillsOptions.START_SKILLS, [])
def test_with_no_start_skills_set_a_new_session_is_asked_for_none(story):
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(story.agents.subject, Ready)


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_start_skill_loaded_by_the_skill_tool_counts_as_read(story):
    story.agent_loads_a_skill(story.agents.subject, JOURNAL_SKILL)
    story.agent_loads_a_skill(story.agents.subject, ETIQUETTE_SKILL)
    story.agent_loads_a_skill(story.agents.subject, MESSAGES_SKILL)
    story.agent_looks_at_the_overview(story.agents.subject)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_one_shell_line_printing_three_skill_files_reads_them_all(story):
    story.agent_has_run_in_the_shell(story.agents.subject, f"cat .claude/skills/{JOURNAL_SKILL}/SKILL.md .claude/skills/{ETIQUETTE_SKILL}/SKILL.md .claude/skills/{MESSAGES_SKILL}/SKILL.md | head -40")
    story.agent_looks_at_the_overview(story.agents.subject)
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_shell_line_that_writes_a_skill_file_elsewhere_reads_nothing(story):
    story.agent_has_run_in_the_shell(story.agents.subject, f"cat .claude/skills/{JOURNAL_SKILL}/SKILL.md > copy.md")
    result = story.agent_reads(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(story.agents.subject, Ready)

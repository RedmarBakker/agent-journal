from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.skills.support.skill_files import HOMES
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.providers.codex import Codex
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.main.session_opening import SessionOpening

JOURNAL_SKILL, ETIQUETTE_SKILL = "journal", "journal-etiquette"


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@provider(Codex)
def test_codex_reading_its_start_skills_through_the_journals_runner_frees_its_tools(story):
    story.agent_cats_a_skill_through_the_runner(story.agents.subject, HOMES[1], JOURNAL_SKILL)
    story.expect_allowed()
    story.agent_cats_a_skill_through_the_runner(story.agents.subject, HOMES[1], ETIQUETTE_SKILL)
    story.agent_looks_at_the_overview(story.agents.subject)
    story.expect_task_made_by(story.agents.subject, story.agent_creates_task(story.agents.subject, "the footer"))
    story.agent_writes(story.agents.subject, "footer.py")
    story.expect_allowed()
    story.expect_agent_not_told(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST)
    story.expect_stack(story.agents.subject, Ready)

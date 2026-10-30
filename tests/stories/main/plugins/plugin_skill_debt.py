from journal.features.skills.feature import Skills
from journal.features.skills.skills_nudges import SkillsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import InstalledPlugin

SKILL = "echo-guide"
OWED = f"the {SKILL} skill, .claude/skills/{SKILL}/SKILL.md"


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_skill_a_plugin_requires_is_owed_once_held_as_the_journals_own_and_paid_by_a_read_of_its_file(story):
    story.user_switches_on(Skills)
    story.expect_project_file(f".claude/skills/{SKILL}/SKILL.md", f"plugin: {story.plugins.first}")
    story.agent_is_prompted(story.agents.subject, "please follow the guide")
    result = story.agent_reads(story.agents.subject)
    result.expect_refused(story.agents.subject, SkillsNudges.SKILL_READ_REQUEST, skills=OWED)
    story.agent_reads_a_skill(story.agents.subject, SKILL)
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.agent_is_prompted(story.agents.subject, "and the guide again")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_skill_of_a_plugin_removed_is_owed_no_longer(story):
    story.user_switches_on(Skills)
    story.agent_is_prompted(story.agents.subject, "please follow the guide")
    story.user_types(f"plugin remove {story.plugins.first}")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)

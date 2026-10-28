from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import InstalledPlugin

SKILL = "echo-guide"
HOMES = (".claude/skills", ".agents/skills")


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plugins_skills_are_published_stamped_go_when_it_is_switched_off_and_come_back_when_on(story):
    for home in HOMES:
        story.expect_project_file(f"{home}/{SKILL}/SKILL.md", f"---\nplugin: {story.start.plugin}\nname: {SKILL}\n")
        story.expect_project_file(f"{home}/{SKILL}/.gitignore", "*")
    story.user_types(f"plugin disable {story.start.plugin}")
    for home in HOMES:
        story.expect_no_project_file(f"{home}/{SKILL}")
    story.user_types(f"plugin enable {story.start.plugin}")
    for home in HOMES:
        story.expect_project_file(f"{home}/{SKILL}/SKILL.md")
    story.expect_stack(Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plugin_removed_takes_its_skills_away(story):
    story.user_types(f"plugin remove {story.start.plugin}")
    for home in HOMES:
        story.expect_no_project_file(f"{home}/{SKILL}")
    story.expect_stack(Ready)

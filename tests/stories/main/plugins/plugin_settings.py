from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import InstalledPlugin


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_installed_plugin_asks_for_its_secret_proposed_for_the_plugin(story):
    story.agent_runs("secret list")
    story.expect_command_text(f"{story.start.plugin} Token")
    story.expect_stack(Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plugin_setting_the_user_configures_follows_the_plugins_schema(story):
    story.user_types(f"plugin configure {story.start.plugin} repeat 3")
    story.expect_command_passed()
    story.user_types(f"plugin configure {story.start.plugin} repeat three")
    story.expect_command_text("repeat is a number; 'three' is not")
    story.user_types(f"plugin configure {story.start.plugin} token abc")
    story.expect_command_text("the user fills it on the Secrets page")
    story.expect_stack(Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_only_the_user_configures_a_plugin(story):
    story.agent_runs(f"plugin configure {story.start.plugin} repeat 2")
    story.expect_command_text("only the user configures")
    story.expect_stack(Ready)

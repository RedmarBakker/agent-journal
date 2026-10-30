from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import InstalledPlugin


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_installed_plugin_asks_for_its_secret_proposed_for_the_plugin(story):
    result = story.agent_runs(story.agents.subject, "secret list")
    result.expect_command_text(f"{story.plugins.first} Token")
    story.expect_stack(story.agents.subject, Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugin_setting_the_user_configures_follows_the_plugins_schema(story):
    result = story.user_types(f"plugin configure {story.plugins.first} repeat 3")
    result.expect_command_passed()
    result = story.user_types(f"plugin configure {story.plugins.first} repeat three")
    result.expect_command_text("repeat is a number; 'three' is not")
    result = story.user_types(f"plugin configure {story.plugins.first} token abc")
    result.expect_command_text("the user fills it on the Secrets page")
    story.expect_stack(story.agents.subject, Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_only_the_user_configures_a_plugin(story):
    result = story.agent_runs(story.agents.subject, f"plugin configure {story.plugins.first} repeat 2")
    result.expect_command_text("only the user configures")
    story.expect_stack(story.agents.subject, Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugins_filled_secret_is_given_to_its_program_only_once_the_user_allows_it(story):
    secret = story.plugin_secret(story.plugins.first)
    variable = story.secret_variable(secret)
    story.user_posted(f"/journal/secrets/{secret}/fill", {"value": "tok_0123456789abcdef", "field": "key"})
    story.agent_creates_task(story.agents.subject, "first")
    story.expect_plugin_given(story.plugins.first, variable, is_given=False)
    story.user_posted(f"/journal/secrets/{secret}", {"programs": [f"plugin:{story.plugins.first}"], "proposed": []})
    story.agent_creates_task(story.agents.subject, "second")
    story.expect_plugin_given(story.plugins.first, variable, is_given=True)
    story.expect_stack(story.agents.subject, Ready)

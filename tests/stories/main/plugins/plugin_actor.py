from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from journal.support.plugin_tokens import PluginTokens
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import InstalledPlugin
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan

PLUGIN = "echo"


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugins_message_is_the_journals_and_made_by_the_plugin(story):
    result = story.plugin_runs(story.plugins.first, "message send 'a word from echo'")
    result.expect_command_passed()
    story.expect_message(story.newest("messages"), author="system", creator=f"plugin:{story.plugins.first}")
    story.expect_stack(story.agents.subject, Ready)


@story(UserDraftedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugin_never_approves_a_plan(story):
    result = story.plugin_runs(PLUGIN, f"plan approve {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text("only the user approves")
    story.expect_task(story.tasks.first, state="open")
    story.expect_task(story.tasks.second, state="open")
    story.expect_stack(story.agents.subject, Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugins_command_with_a_wrong_token_or_another_plugins_name_is_refused(story):
    result = story.plugin_runs_with_token(story.plugins.first, "wrong", "task list")
    result.expect_command_refused()
    result = story.plugin_runs_with_token("lint", story.app.container.get(PluginTokens).build(story.plugins.first), "task list")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugins_answer_to_a_new_task_shows_its_card_and_runs_its_command_as_the_plugin(story):
    task = story.agent_creates_task(story.agents.subject, "echo me")
    story.expect_task_logged(task, "echoed")
    story.expect_newest_message_text(f"Echoed task {task}")
    story.expect_message(story.newest("messages"), creator=f"plugin:{story.plugins.first}")
    story.expect_stack(story.agents.subject, Ready)

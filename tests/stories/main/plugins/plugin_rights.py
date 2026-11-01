from journal.features.plugins.plugins_nudges import PluginsNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import ECHO, InstalledPlugin
from tests.stories.fixtures.main.working_agent import WorkingAgent

PLUGINS = "." + "journal/" + "plugins"


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_agent_may_not_install_a_plugin_and_proposes_it_to_the_user_instead(story):
    result = story.agent_runs(story.agents.subject, f"plugin install {ECHO} --yes")
    result.expect_command_text("only the user installs a plugin: `journal plugin propose")
    story.agent_runs(story.agents.subject, f"plugin propose {ECHO} --why 'to echo'")
    story.expect_newest_message_text("The agent proposes the plugin echo: to echo")
    story.expect_stack(story.agents.subject, Ready)


@story(InstalledPlugin, subject=AgentRole.MAIN)
def test_the_agent_may_switch_a_plugin_off_but_only_the_user_switches_it_on(story):
    story.agent_runs(story.agents.subject, f"plugin disable {story.plugins.first}")
    result = story.agent_runs(story.agents.subject, f"plugin enable {story.plugins.first}")
    result.expect_command_text("only the user switches on")
    story.expect_stack(story.agents.subject, Ready)


@story(InstalledPlugin, subject=AgentRole.MAIN)
def test_the_agent_may_run_an_installed_plugins_program_but_never_write_to_its_files(story):
    installed = f"{PLUGINS}/{story.plugins.first}"
    result = story.agent_writes(story.agents.subject, f"{story.project_root()}/{installed}/run.py")
    result.expect_refused(story.agents.subject, PluginsNudges.PLUGIN_FILE_OWNERSHIP)
    result = story.agent_runs_in_the_shell(story.agents.subject, f"{installed}/bin/judge --changes > /tmp/judged.txt 2>&1")
    result.expect_allowed()
    story.expect_plugin_given(story.plugins.first, "PYTHONDONTWRITEBYTECODE", is_given=True)
    result = story.agent_runs_in_the_shell(story.agents.subject, f"echo hi > {installed}/run.py")
    result.expect_refusal_text("plugin's files")
    result = story.agent_runs_in_the_shell(story.agents.subject, f"rm -rf {installed}")
    result.expect_refusal_text("plugin's files")
    story.expect_stack(story.agents.subject, Ready)

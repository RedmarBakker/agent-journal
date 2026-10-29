from journal.features.plugins.plugins_nudges import PluginsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import ECHO, InstalledPlugin
from tests.stories.fixtures.main.working_agent import WorkingAgent

PLUGINS = "." + "journal/" + "plugins"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_agent_may_not_install_a_plugin_and_proposes_it_to_the_user_instead(story):
    story.agent_runs(f"plugin install {ECHO} --yes")
    story.expect_command_text("only the user installs a plugin: `journal plugin propose")
    story.agent_runs(f"plugin propose {ECHO} --why 'to echo'")
    story.expect_newest_message_text("The agent proposes the plugin echo: to echo")
    story.expect_stack(Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_agent_may_switch_a_plugin_off_but_only_the_user_switches_it_on(story):
    story.agent_runs(f"plugin disable {story.fixture.plugin}")
    story.agent_runs(f"plugin enable {story.fixture.plugin}")
    story.expect_command_text("only the user switches on")
    story.expect_stack(Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_agent_may_run_an_installed_plugins_program_but_never_write_to_its_files(story):
    installed = f"{PLUGINS}/{story.fixture.plugin}"
    story.agent_writes(f"{story.project_root()}/{installed}/run.py")
    story.expect_refused(PluginsNudges.PLUGIN_FILE_OWNERSHIP)
    story.agent_runs_in_the_shell(f"{installed}/bin/judge --changes > /tmp/judged.txt 2>&1")
    story.expect_allowed()
    story.agent_runs_in_the_shell(f"echo hi > {installed}/run.py")
    story.expect_refusal_text("plugin's files")
    story.agent_runs_in_the_shell(f"rm -rf {installed}")
    story.expect_refusal_text("plugin's files")
    story.expect_stack(Ready)

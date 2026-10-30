from journal.features.plugins.plugins_nudges import PluginsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.copied_plugin import CopiedPlugin
from tests.stories.fixtures.main.installed_plugin import ECHO

REPEAT_MINUTES = PluginsNudges.PLUGIN_BROKEN.repeat.amount
WORKING_MANIFEST = (ECHO / "journal-plugin.json").read_text()


@story(CopiedPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugin_that_stops_working_is_named_once_again_when_its_fault_changes_or_a_day_passes_and_no_more_once_fixed(story):
    story.plugin_manifest_written(story.plugins.first, "{ not json")
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_agent_told(story.agents.subject, PluginsNudges.PLUGIN_BROKEN, plugin=story.plugins.first)
    story.agent_is_quiet_for(story.agents.subject, 2)
    story.expect_agent_not_told(story.agents.subject, PluginsNudges.PLUGIN_BROKEN, plugin=story.plugins.first)
    story.plugin_manifest_written(story.plugins.first, "not json at all")
    story.agent_is_quiet_for(story.agents.subject, 3)
    story.expect_agent_told(story.agents.subject, PluginsNudges.PLUGIN_BROKEN, plugin=story.plugins.first)
    story.time_travel(minutes=REPEAT_MINUTES)
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_agent_told(story.agents.subject, PluginsNudges.PLUGIN_BROKEN, plugin=story.plugins.first)
    story.plugin_manifest_written(story.plugins.first, WORKING_MANIFEST)
    story.time_travel(minutes=REPEAT_MINUTES)
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_agent_not_told(story.agents.subject, PluginsNudges.PLUGIN_BROKEN, plugin=story.plugins.first)
    story.expect_stack(story.agents.subject, Ready)


@story(CopiedPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugin_the_user_switched_off_is_never_named_as_broken(story):
    story.user_types(f"plugin disable {story.plugins.first}")
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_agent_not_told(story.agents.subject, PluginsNudges.PLUGIN_BROKEN, plugin=story.plugins.first)
    story.expect_stack(story.agents.subject, Ready)

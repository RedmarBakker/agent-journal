from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import InstalledPlugin


@story(InstalledPlugin, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_plugins_page_lists_a_plugin_switches_it_off_and_removes_it(story):
    plugin = story.plugin_number(story.plugins.first)
    result = story.user_opens("/journal/plugins")
    result.expect_viewer_rows("rows", "status", ["on"])
    story.user_presses(f"/journal/plugins/{plugin}/disable", {})
    result = story.user_opens("/journal/plugins")
    result.expect_viewer_rows("rows", "status", ["off"])
    story.user_presses(f"/journal/plugins/{plugin}/remove", {})
    result = story.user_opens("/journal/plugins")
    result.expect_viewer_rows("rows", "name", [])
    story.expect_stack(story.agents.subject, Ready)

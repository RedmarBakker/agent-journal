"""Publishes a plugin from a throwaway git repository of the story's temp folder, so it runs only with JOURNAL_PROCESS_STORIES set, never in the default story run."""
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

PLUGIN = "tagged"
INSTALLED = "1.0.0"
RELEASED = "2.0.0"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_journal_update_offers_a_plugin_update_and_only_its_install_applies_it(story):
    story.plugin_release_published(INSTALLED)
    plugin = story.user_posted("/journal/plugins", {"source": story.plugin_source()})["id"]
    story.plugin_release_published(RELEASED)
    story.journal_starts_after_an_update()
    story.expect_plugin_update_offered(PLUGIN, INSTALLED, RELEASED)
    story.expect_plugin_version(plugin, INSTALLED)
    preview = story.user_posted(f"/journal/plugins/{plugin}/upgrade-preview", {})
    story.expect_plugin_version(plugin, INSTALLED)
    story.user_posted(f"/journal/plugins/{plugin}/upgrade", {"ref": preview["commit"]})
    story.expect_plugin_version(plugin, RELEASED)
    story.expect_stack(story.agents.subject, Ready)

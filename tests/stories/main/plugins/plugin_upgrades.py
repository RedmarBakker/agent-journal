import json

from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from journal.version import VERSION
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

MANIFEST = {"name": "held", "version": "1", "program": "run.py", "hears": ["tool_starting"]}
NEWER_JOURNAL = "99.0.0"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plugin_whose_new_version_needs_a_newer_journal_stays_at_its_version_and_says_which_it_waits_for(story):
    story.project_file_holding("held/run.py", "print()")
    story.project_file_holding("held/journal-plugin.json", json.dumps(MANIFEST))
    story.user_types(f"plugin install {story.project_root()}/held --yes")
    story.project_file_holding("held/journal-plugin.json", json.dumps({**MANIFEST, "version": "2", "journal": NEWER_JOURNAL}))
    story.agent_runs("plugin upgrade held --yes")
    story.agent_runs("plugin list")
    story.expect_command_text(f"waits for journal {NEWER_JOURNAL}")
    story.project_file_holding("held/journal-plugin.json", json.dumps({**MANIFEST, "version": "3", "journal": VERSION}))
    story.agent_runs("plugin upgrade held --yes")
    story.agent_runs("plugin list")
    story.expect_command_text_without("waits for journal")
    story.expect_stack(Ready)

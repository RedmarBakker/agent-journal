import json
from pathlib import Path

from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

ECHO = Path(__file__).parents[3] / "plugins" / "echo"
BAD_MANIFEST = {"name": "bad", "version": "1", "program": "run.py", "hears": ["nothing"]}


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plugin_is_previewed_then_installed_from_a_folder_on_and_never_twice(story):
    story.user_types(f"plugin install {ECHO}")
    story.expect_command_text("echo 1.0.0")
    story.expect_command_text("runs for each event it hears, from its folder: run.py")
    story.expect_command_text("holds before the agent continues: tool_starting, prompt_submitted")
    story.expect_command_text("nothing installed yet")
    story.agent_runs("plugin list")
    story.expect_command_text_without("echo")
    story.user_types(f"plugin install {ECHO} --yes")
    story.expect_command_text("installed echo, on")
    story.agent_runs("plugin list")
    story.expect_command_text("echo")
    story.user_types(f"plugin install {ECHO} --yes")
    story.expect_command_text("installed already")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plugin_whose_manifest_hears_no_event_is_refused_and_nothing_is_installed(story):
    story.project_file_holding("bad/journal-plugin.json", json.dumps(BAD_MANIFEST))
    story.project_file_holding("bad/run.py", "")
    story.user_types(f"plugin install {story.project_root()}/bad --yes")
    story.expect_command_refused()
    story.expect_command_text("hears nothing, which is no event")
    story.agent_runs("plugin list")
    story.expect_command_text_without("bad")
    story.expect_stack(Ready)

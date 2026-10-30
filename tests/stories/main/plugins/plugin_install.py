import json
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import ECHO
from tests.stories.fixtures.main.working_agent import WorkingAgent

BAD_MANIFEST = {"name": "bad", "version": "1", "program": "run.py", "hears": ["nothing"]}


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugin_is_previewed_then_installed_from_a_folder_on_and_never_twice(story):
    result = story.user_types(f"plugin install {ECHO}")
    result.expect_command_text("echo 1.0.0")
    result.expect_command_text("runs for each event it hears, from its folder: run.py")
    result.expect_command_text("holds before the agent continues: tool_starting, prompt_submitted")
    result.expect_command_text("nothing installed yet")
    result = story.agent_runs(story.agents.subject, "plugin list")
    result.expect_command_text_without("echo")
    result = story.user_types(f"plugin install {ECHO} --yes")
    result.expect_command_text("installed echo, on")
    result = story.agent_runs(story.agents.subject, "plugin list")
    result.expect_command_text("echo")
    result = story.user_types(f"plugin install {ECHO} --yes")
    result.expect_command_text("installed already")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plugin_whose_manifest_hears_no_event_is_refused_and_nothing_is_installed(story):
    story.project_file_holding("bad/journal-plugin.json", json.dumps(BAD_MANIFEST))
    story.project_file_holding("bad/run.py", "")
    result = story.user_types(f"plugin install {story.project_root()}/bad --yes")
    result.expect_command_refused()
    result.expect_command_text("hears nothing, which is no event")
    result = story.agent_runs(story.agents.subject, "plugin list")
    result.expect_command_text_without("bad")
    story.expect_stack(story.agents.subject, Ready)

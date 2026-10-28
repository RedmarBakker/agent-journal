from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.installed_plugin import InstalledPlugin

FILES = {"type": "heading", "text": "Files", "level": 3}


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plugins_dashboard_is_written_by_its_program_alone(story):
    story.agent_runs("dashboard set a.py a.py")
    story.expect_command_text("written by its plugin's program")
    story.user_opens(f"/journal/plugins/{story.plugin_number(story.start.plugin)}/dashboard")
    story.expect_viewer_shows("pages", None)
    story.expect_stack(Ready)


@story(InstalledPlugin, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plugins_dashboard_is_drawn_from_the_lines_it_wrote_one_line_per_key_rewritten_in_place(story):
    story.plugin_runs(story.start.plugin, "dashboard set a.py a.py --badge '2 sins' --tone warn --heading Files")
    story.plugin_runs(story.start.plugin, "dashboard set b.py b.py --badge clean --tone good --heading Files")
    story.plugin_runs(story.start.plugin, "dashboard set a.py a.py --badge '1 sin' --tone warn --heading Files")
    story.user_opens(f"/journal/plugins/{story.plugin_number(story.start.plugin)}/dashboard")
    story.expect_viewer_part(("pages", "start", "view", "children"), [FILES, {"type": "list", "items": [{"label": "a.py", "badge": "1 sin", "tone": "warn", "note": ""}, {"label": "b.py", "badge": "clean", "tone": "good", "note": ""}]}])
    story.expect_stack(Ready)

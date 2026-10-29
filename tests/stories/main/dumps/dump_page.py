from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_dump_is_dropped_with_files_named_stopped_and_dismissed_from_the_viewer(story):
    dump = story.user_starts_a_dump("some ideas")
    story.user_drops_a_file_in_the_dump(dump, "a.txt", b"hello")
    story.expect_viewer_shows("title", f"Dump {dump}")
    story.expect_viewer_shows("files", ["a.txt"])
    story.user_presses(f"/journal/dumps/{dump}/name", {"title": "Ideas"})
    story.expect_viewer_shows("title", "Ideas")
    story.user_presses(f"/journal/dumps/{dump}/stop", {})
    story.expect_viewer_shows("stopped", True)
    story.user_drops_a_file_in_the_dump(dump, "b.txt", b"more")
    story.expect_viewer_refused("")
    story.user_presses(f"/journal/dumps/{dump}/dismiss", {})
    story.expect_viewer_shows("dismissed", True)
    story.expect_stack(story.agents.subject, Ready)

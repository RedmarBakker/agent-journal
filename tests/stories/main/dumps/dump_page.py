from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.dump_with_a_file import DumpWithAFile


@story(DumpWithAFile, subject=AgentRole.MAIN)
def test_a_dump_is_dropped_with_files_named_stopped_and_dismissed_from_the_viewer(story):
    dump = story.newest("dumps")
    result = story.user_drops_a_file_in_the_dump(dump, "b.txt", b"more")
    result.expect_viewer_shows("title", f"Dump {dump}")
    result.expect_viewer_shows("files", ["a.txt", "b.txt"])
    result = story.user_presses(f"/journal/dumps/{dump}/name", {"title": "Ideas"})
    result.expect_viewer_shows("title", "Ideas")
    result = story.user_presses(f"/journal/dumps/{dump}/stop", {})
    result.expect_viewer_shows("stopped", True)
    result = story.user_drops_a_file_in_the_dump(dump, "c.txt", b"later")
    result.expect_viewer_refused("")
    result = story.user_presses(f"/journal/dumps/{dump}/dismiss", {})
    result.expect_viewer_shows("dismissed", True)
    story.expect_stack(story.agents.subject, Ready)

from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_library_page_reads_the_connection_without_its_token_and_publishes_and_imports_as_the_command_does(story):
    story.user_opens("/journal/library")
    story.expect_viewer_shows("connected", False)
    story.user_connects_to_a_library()
    story.user_opens("/journal/library")
    story.expect_viewer_shows("connected", True)
    story.expect_viewer_shows("name", "Ada")
    story.expect_viewer_shows("token", "")
    story.user_types("sequence create 'Morning Check' --steps look")
    sequence = story.created_number("sequence")
    story.user_presses("/journal/library/items/sequence/publish", {"reference": str(sequence), "note": "first"})
    story.expect_viewer_shows("number", 1)
    story.user_presses("/journal/library/items/sequence/morning-check/import", {})
    story.expect_viewer_passed()
    story.user_opens("/journal/library/items?type=sequence")
    story.expect_viewer_part(("items", 0, "imported_version"), 1)
    story.user_opens("/journal/library/items/sequence/morning-check")
    story.expect_viewer_part(("versions", 0, "note"), "first")
    story.user_presses("/journal/library/items/sequence/morning-check/update", {})
    story.expect_viewer_refused("")
    story.expect_stack(story.agents.subject, Ready)

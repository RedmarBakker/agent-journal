from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

DOCUMENT = "release-notes.md"
DOCUMENT_BYTES = "# Release notes\n\nOne line per change, ünïcode kept.\n".encode()
PICTURE = "logo.png"
PICTURE_BYTES = bytes(range(256)) * 4


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_document_and_a_binary_file_go_through_the_library_byte_for_byte_and_no_markdown_is_no_document(story):
    story.the_project_holds_a_file(DOCUMENT, DOCUMENT_BYTES)
    story.the_project_holds_a_file(PICTURE, PICTURE_BYTES)
    story.user_connects_to_a_library()
    story.user_types(f"library publish document {DOCUMENT}")
    story.expect_command_passed()
    story.user_types(f"library publish document {PICTURE}")
    story.expect_command_refused()
    story.expect_command_text("publish logo.png as a file")
    story.user_types(f"library publish file {PICTURE}")
    story.expect_command_passed()
    story.the_project_file_is_removed(DOCUMENT)
    story.the_project_file_is_removed(PICTURE)
    story.user_types("library import document release-notes.md")
    story.expect_command_passed()
    story.user_types("library import file logo.png")
    story.expect_command_passed()
    story.expect_project_file_holds(DOCUMENT, DOCUMENT_BYTES)
    story.expect_project_file_holds(PICTURE, PICTURE_BYTES)
    story.expect_stack(story.agents.subject, Ready)

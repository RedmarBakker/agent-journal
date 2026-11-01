import json

from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.message_with_file import FILE, MessageWithFile
from tests.stories.fixtures.main.working_agent import WorkingAgent

FINDINGS = "# Findings\n\nThe cleanup pluralises the wrong noun.\n"


def old_document(n: int, title: str, deleted: float) -> str:
    return "---\n" + json.dumps({"n": n, "title": title, "abstract": "what is broken", "deleted": deleted}) + "\n---\n" + FINDINGS


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_version_3_documents_are_brought_in_once_for_the_whole_project_and_found_by_their_words(story):
    story.project_file_holding("old/001/doc.md", old_document(1, "Audit of the package", 0))
    story.project_file_holding("old/002/doc.md", old_document(2, "Gone", 1.0))
    story.project_file_holding("old/003/doc.md", "")
    result = story.user_types(f"doc import {story.project_root()}/old")
    result.expect_command_text("1 documents brought in, 0 already here")
    result = story.user_types(f"doc import {story.project_root()}/old")
    result.expect_command_text("0 documents brought in, 1 already here")
    other = story.another_environment("other")
    result = story.user_opens_in(other, "/journal/docs")
    result.expect_viewer_rows("rows", "title", ["Audit of the package"])
    result = story.user_opens("/journal/docs/search?words=pluralises+noun")
    result.expect_viewer_first_hit(story.newest("docs"), "pluralises the wrong noun")
    story.expect_stack(story.agents.subject, Ready)


@story(MessageWithFile, subject=AgentRole.MAIN)
def test_a_file_attached_to_a_message_is_listed_on_the_documents_page_by_its_type_and_words(story):
    result = story.user_opens("/journal/attachments?file_type=images")
    result.expect_viewer_shows("total", 1)
    result.expect_viewer_part(("files", 0, "name"), FILE)
    result = story.user_opens(f"/journal/messages?ids={story.messages.first}")
    result.expect_viewer_part(("rows", 0, "files"), [FILE])
    result = story.user_opens("/journal/attachments?file_type=other")
    result.expect_viewer_shows("total", 0)
    result = story.user_opens("/journal/attachments?search=footer")
    result.expect_viewer_shows("total", 1)
    story.expect_stack(story.agents.subject, Ready)

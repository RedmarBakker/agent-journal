from journal.features.docs.docs_options import DocsOptions
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.written_document import TEXT, WrittenDocument

WITH_RISKS = TEXT + "\n## Risks\n\nNone\n"


@story(WrittenDocument, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(DocsOptions.REVISION_WINDOW, 30)
def test_edits_within_the_window_fold_into_one_revision_until_it_is_kept(story):
    document = story.documents.first
    story.agent_rewrites_the_document(story.agents.subject, document, WITH_RISKS)
    story.agent_rewrites_the_document(story.agents.subject, document, WITH_RISKS)
    result = story.agent_runs(story.agents.subject, f"doc revisions {document}")
    result.expect_command_line_count(1)
    result.expect_command_text("added Risks")
    result = story.agent_runs(story.agents.subject, f"doc keep {document}")
    result.expect_command_text(f"revision 1 of doc {document} kept; the next edit opens revision 2")
    result = story.agent_runs(story.agents.subject, f"doc keep {document}")
    result.expect_command_text(f"revision 1 of doc {document} is already saved")
    story.agent_rewrites_the_document(story.agents.subject, document, TEXT)
    result = story.agent_runs(story.agents.subject, f"doc revisions {document}")
    result.expect_command_line_count(2)
    result = story.agent_runs(story.agents.subject, f"doc revision {document} 1")
    result.expect_command_text("## Risks")
    result = story.agent_runs(story.agents.subject, f"doc revision {document} 3")
    result.expect_command_text(f"doc {document} has revisions 1 to 2")
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(WrittenDocument, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(DocsOptions.REVISION_WINDOW, 0)
def test_with_no_window_each_edit_opens_the_next_revision_and_the_page_cannot_keep_one_kept(story):
    document = story.documents.first
    story.agent_rewrites_the_document(story.agents.subject, document, WITH_RISKS)
    story.agent_rewrites_the_document(story.agents.subject, document, TEXT)
    result = story.user_opens(f"/journal/docs/{document}/revisions")
    result.expect_viewer_list_count(2)
    result = story.user_presses(f"/journal/docs/{document}/keep", {})
    result.expect_viewer_refused("")
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)

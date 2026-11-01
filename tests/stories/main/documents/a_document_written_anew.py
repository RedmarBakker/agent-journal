from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.written_document import ABSTRACT, TITLE, WrittenDocument


@story(WrittenDocument, subject=AgentRole.MAIN)
def test_a_document_written_anew_from_a_file_takes_its_text_and_keeps_its_title_and_abstract(story):
    result = story.agent_rewrites_the_document(story.agents.subject, story.documents.first, "## One\n\nthe words as ruled")
    result.expect_command_text(f"doc {story.documents.first} written anew: {TITLE}")
    result = story.agent_runs(story.agents.subject, f"doc show {story.documents.first} --section 1")
    result.expect_command_text("the words as ruled")
    result.expect_command_text(ABSTRACT)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)

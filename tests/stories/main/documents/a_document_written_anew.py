from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.written_document import ABSTRACT, TITLE, WrittenDocument


@story(WrittenDocument, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_document_written_anew_from_a_file_takes_its_text_and_keeps_its_title_and_abstract(story):
    story.agent_rewrites_the_document(story.agents.subject, story.fixture.document, "## One\n\nthe words as ruled")
    story.expect_command_text(f"doc {story.fixture.document} written anew: {TITLE}")
    story.agent_runs(story.agents.subject, f"doc show {story.fixture.document} --section 1")
    story.expect_command_text("the words as ruled")
    story.expect_command_text(ABSTRACT)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)

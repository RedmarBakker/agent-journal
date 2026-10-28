from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_document_written_anew_from_a_file_takes_its_text_and_keeps_its_title_and_abstract(story):
    document = story.agent_writes_a_document("A proposal", "what it proposes", "## One\n\nthe first words")
    story.agent_rewrites_the_document(document, "## One\n\nthe words as ruled")
    story.expect_command_text(f"doc {document} written anew: A proposal")
    story.agent_runs(f"doc show {document} --section 1")
    story.expect_command_text("the words as ruled")
    story.expect_command_text("what it proposes")
    story.expect_stack(Ready, FollowingSequence)

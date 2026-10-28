from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.written_document import WrittenDocument
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WrittenDocument, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_document_is_docked_and_undocked_from_its_inspector_by_the_same_card(story):
    story.user_docks("docs", story.start.document)
    story.expect_viewer_passed()
    card = story.docked_card()
    story.expect_card(card, docked=True, row=f"docs:{story.start.document}")
    story.user_undocks("docs", story.start.document)
    story.expect_card(card, docked=False)
    story.expect_stack(Ready, FollowingSequence)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_row_that_cannot_be_docked_is_refused_by_the_viewer(story):
    story.user_docks("environments", 1)
    story.expect_viewer_refused("")
    story.expect_stack(Ready)

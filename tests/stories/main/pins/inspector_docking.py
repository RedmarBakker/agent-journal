from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.written_document import WrittenDocument
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WrittenDocument, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_document_is_docked_and_undocked_from_its_inspector_by_the_same_card(story):
    result = story.user_docks("docs", story.documents.first)
    result.expect_viewer_passed()
    card = story.docked_card()
    story.expect_card(card, docked=True, row=f"docs:{story.documents.first}")
    story.user_undocks("docs", story.documents.first)
    story.expect_card(card, docked=False)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_row_that_cannot_be_docked_is_refused_by_the_viewer(story):
    result = story.user_docks("environments", 1)
    result.expect_viewer_refused("")
    story.expect_stack(story.agents.subject, Ready)

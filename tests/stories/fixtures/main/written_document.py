from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture

TITLE, ABSTRACT, TEXT = "the footer", "where the links go", "## Layout\n\nThe footer holds the links.\n"


class WrittenDocument(StateFixture):
    """The agent wrote a document from a file, which started the sequence a new document starts: start.document."""

    stack = (Ready, FollowingSequence)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.document = story.agent_writes_a_document(TITLE, ABSTRACT, TEXT)

    def expected(self, story) -> None:
        story.expect_stack(Ready, FollowingSequence)

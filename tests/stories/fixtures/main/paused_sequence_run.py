from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.sequence_run import SequenceRun
from tests.stories.fixtures.state_fixture import StateFixture


class PausedSequenceRun(StateFixture):
    """The agent took up the first step of the running release sequence and paused the run, saying why: start.sequence."""

    stack = (Ready, FollowingSequence)

    parent = SequenceRun

    def steps(self, story) -> None:
        story.agent_runs("sequence follow")
        story.agent_runs("sequence pause --why 'the user wants the footer first'")

    def expected(self, story) -> None:
        story.expect_command_passed()
        story.expect_stack(Ready, FollowingSequence)

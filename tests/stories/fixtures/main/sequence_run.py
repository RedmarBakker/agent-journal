from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.working_agent import WorkingAgent


class SequenceRun(StateFixture):
    """The agent at work wrote the release sequence and started it, its first step said: start.sequence."""

    stack = (Ready, FollowingSequence)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.sequence = story.agent_creates_sequence("release", "raise the version | push the tag")
        story.agent_runs(f"sequence run {self.sequence}")

    def expected(self, story) -> None:
        story.expect_agent_told(SequencesNudges.PENDING_STEP, n=self.sequence, step=1)
        story.expect_stack(Ready, FollowingSequence)

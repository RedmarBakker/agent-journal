from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.working_agent import WorkingAgent


class SequenceRun(StateFixture):
    """The agent at work wrote the release sequence and started it, its first step said: story.sequences.first."""

    stack = (Ready, FollowingSequence)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.sequences.first = story.agent_creates_sequence(story.agents.main, "release", "raise the version | push the tag")
        story.agent_runs(story.agents.main, f"sequence run {self.sequences.first}")

    def expected(self, story) -> None:
        story.expect_agent_told(story.agents.main, SequencesNudges.PENDING_STEP, n=self.sequences.first, step=1)
        story.expect_stack(story.agents.main, Ready, FollowingSequence)

from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class GuardedSequenceRun(StateFixture):
    """The agent at work wrote a release sequence whose first step holds file edits and lets git status through, and started it, its first step said: start.sequence."""

    stack = (Ready, FollowingSequence)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.agent_runs("sequence create 'release' --step 'Check | look at the status first' --hold-edits --allow-commands 'git status*' --step 'Tag | push the tag'")
        self.sequence = story.created_number("sequence")
        story.agent_runs(f"sequence run {self.sequence}")

    def expected(self, story) -> None:
        story.expect_command_passed()
        story.expect_stack(Ready, FollowingSequence)

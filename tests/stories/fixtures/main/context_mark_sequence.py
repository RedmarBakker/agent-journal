from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.sequence_run import SequenceRun
from tests.stories.fixtures.state_fixture import StateFixture


class ContextMarkSequence(StateFixture):
    """The agent following the release sequence reached the first context mark, and weighs its memories on top of the sequence."""

    stack = (Ready, FollowingSequence, WeighingMemories)

    parent = SequenceRun

    def steps(self, story) -> None:
        story.agent_consumes_context(MemoryThresholds.CONTEXT[0])

    def expected(self, story) -> None:
        story.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=MemoryThresholds.CONTEXT[0])
        story.expect_stack(Ready, FollowingSequence, WeighingMemories)

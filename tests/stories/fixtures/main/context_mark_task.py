from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class ContextMarkTask(StateFixture):
    """The agent at work on its started task reached the first context mark, and weighs its memories before it may write."""

    stack = (Ready, Working, WeighingMemories)

    parent = StartedTask

    def steps(self, story) -> None:
        story.agent_consumes_context(MemoryThresholds.CONTEXT[0])

    def expected(self, story) -> None:
        story.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=MemoryThresholds.CONTEXT[0])
        story.expect_stack(Ready, Working, WeighingMemories)

from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.events.rows.context_decided import ContextDecided
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_part import MemoryPart


@dataclass(frozen=True)
class WeighingMemories(BaseState):
    """At a mark of the context window the agent weighs its memories: writes wait and a stop is refused, reads and journal commands go through, and journal memory add, weigh, remove or skip pops it; a state above it that pops brings it back while the mark is owed, and a compaction over it, which clears the mark owed, pops it once it ends."""

    name = "weighing_memories"
    title = "Weighing memories"
    percent: int = 0

    def takes_pushes(self) -> bool:
        return False

    def wait_description(self) -> tuple[str, str]:
        return f"weighing its memories at {self.percent}% of the context", ""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return self.refuse(MemoryNudges.DECISION_EDIT_BLOCK.create()) if event.call.writes else self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.refuse(MemoryNudges.UNDECIDED_STOP.create(percent=self.percent))

    def on_context_decided(self, event: ContextDecided, settings: Settings) -> Transition:
        return self.pop()

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...] | Transition:
        return () if data.part(MemoryPart).threshold_due else self.pop()

from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.tool_finished import ToolFinished
from journal.features.memory.memory_conduct import threshold_check
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_part import MemoryPart

CLOCK_IN = "clock-in"


class WorkerMemoryConduct(Conduct):
    """The memory feature's conduct toward a worker: its own memories by weight once its journal clock-in has run, on its first job or a next one sent to it, and WeighingMemories pushed over its work at a mark of its own context window."""

    def on_agent_event(self, event: AgentEvent, settings: Settings) -> Transition:
        return threshold_check(self, event, settings)

    def on_tool_finished(self, event: ToolFinished, settings: Settings) -> Transition:
        if event.subagent or not event.call.is_journal_noun(CLOCK_IN):
            return self.none()
        shown = event.data.part(MemoryPart).shown
        if not shown:
            return self.none()
        return self.none(MemoryNudges.OWN_MEMORIES.create(memories="; ".join(shown)))

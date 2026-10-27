from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.memory.support.memory_ends import MemoryEnds


class MemoryMomentEnd(AgentListener[Ticked]):
    """At each tick the memories whose moment has passed are removed."""

    def __init__(self, ends: MemoryEnds) -> None:
        self.ends = ends

    def handle(self, event: Ticked) -> None:
        self.ends.moment_passed(event.environment_id, event.time)

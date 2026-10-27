from journal.events.listener import Listener
from journal.events.rows.plan_finished import PlanFinished
from journal.features.memory.support.memory_ends import MemoryEnds


class MemoryPlanEnd(Listener[PlanFinished]):
    """A plan done removes the memories that end with it."""

    def __init__(self, ends: MemoryEnds) -> None:
        self.ends = ends

    def handle(self, event: PlanFinished) -> None:
        self.ends.row_closed(event.environment_id, f"plans:{event.plan_id}", event.time)

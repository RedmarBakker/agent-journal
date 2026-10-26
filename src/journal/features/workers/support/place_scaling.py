from dataclasses import dataclass

from journal.models.support.agent_load import AgentLoad


@dataclass(frozen=True)
class PlaceScaling:
    """When the load changes the workers out at once: one place more once the load has stayed over the scale-up level for its dwell, and as long since the last change, up to the user's ceiling; one fewer once it has stayed under the scale-down level for its dwell, and as long since the last change, down to the floor, never while a worker holds a task or anything waits. The gap between the levels and the dwells keep it from flapping."""

    up_dwell_minutes: float
    down_dwell_minutes: float
    floor: int
    ceiling: int

    def opens(self, queue: AgentLoad, places: int, moment: float) -> bool:
        return places < self.ceiling and queue.busy_minutes >= self.up_dwell_minutes and self.dwelt(queue, moment, self.up_dwell_minutes)

    def closes(self, queue: AgentLoad, places: int, has_worker_task: bool, moment: float) -> bool:
        return places > self.floor and not has_worker_task and not queue.waiting and queue.low_minutes >= self.down_dwell_minutes and self.dwelt(queue, moment, self.down_dwell_minutes)

    @staticmethod
    def dwelt(queue: AgentLoad, moment: float, minutes: float) -> bool:
        return moment - queue.scaled_at >= minutes * 60

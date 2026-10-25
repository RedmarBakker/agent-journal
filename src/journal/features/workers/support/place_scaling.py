from dataclasses import dataclass

from journal.models.support.agent_load import AgentLoad


@dataclass(frozen=True)
class PlaceScaling:
    """When the load changes the workers out at once: one place more once the load has stayed over the scale-up level for its dwell, and as long since the last change, up to the user's ceiling; one fewer once it has stayed under the scale-down level for its dwell, and as long since the last change, down to the floor, never while a worker holds a task or anything waits. The gap between the levels and the dwells keep it from flapping."""

    up_dwell_minutes: float
    down_dwell_minutes: float
    floor: int
    ceiling: int

    def opens(self, load: AgentLoad, places: int, now: float) -> bool:
        return places < self.ceiling and load.over_minutes >= self.up_dwell_minutes and self.dwelt(load, now, self.up_dwell_minutes)

    def closes(self, load: AgentLoad, places: int, holding: bool, now: float) -> bool:
        return places > self.floor and not holding and not load.waiting and load.under_minutes >= self.down_dwell_minutes and self.dwelt(load, now, self.down_dwell_minutes)

    @staticmethod
    def dwelt(load: AgentLoad, now: float, minutes: float) -> bool:
        return now - load.scaled_at >= minutes * 60

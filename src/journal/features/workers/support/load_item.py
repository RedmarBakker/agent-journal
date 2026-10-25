from dataclasses import dataclass


@dataclass(frozen=True)
class LoadItem:
    """One item that waits on the orchestrator: the row it is about, as workers:12 or messages:553, when it arrived, when it was cleared (0 while it waits), and its weight in the load."""

    ref: str
    arrived_at: float
    weight: float
    cleared_at: float = 0.0

    def is_waiting(self, time: float) -> bool:
        return self.arrived_at <= time and not (self.cleared_at and self.cleared_at <= time)

    def is_cleared_in(self, start: float, end: float) -> bool:
        return bool(self.cleared_at) and start < self.cleared_at <= end

    def cleared(self, time: float) -> "LoadItem":
        return LoadItem(self.ref, self.arrived_at, self.weight, time)

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class LoadItem:
    """One worker or user message counted in a queue's load, with when it arrived, was cleared or ended, and its weight."""

    ref: str
    arrived_at: float
    weight: float
    cleared_at: float = 0.0
    ended_at: float = 0.0

    def is_waiting(self, time: float) -> bool:
        return self.arrived_at <= time and not (self.cleared_at and self.cleared_at <= time) and not (self.ended_at and self.ended_at <= time)

    def is_cleared_in(self, start: float, end: float) -> bool:
        return bool(self.cleared_at) and start < self.cleared_at <= end

    def cleared(self, time: float) -> "LoadItem":
        return replace(self, cleared_at=time)

    def ended(self, time: float) -> "LoadItem":
        return replace(self, ended_at=time)

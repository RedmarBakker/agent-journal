from dataclasses import dataclass, replace


@dataclass(frozen=True)
class LoadItem:
    """One item that waits on the orchestrator: the row it is about, as workers:12 or messages:553, when it arrived, when it was cleared, by a merge, a checked proof or a reply (0 while it waits), when it ended without a clearing, by a send-back, a release or a stop, its weight in the load, and whether it is a return after a send-back, a clash or a sin rather than a job's first report."""

    ref: str
    arrived_at: float
    weight: float
    cleared_at: float = 0.0
    is_repeat: bool = False
    ended_at: float = 0.0

    def is_waiting(self, time: float) -> bool:
        return self.arrived_at <= time and not (self.cleared_at and self.cleared_at <= time) and not (self.ended_at and self.ended_at <= time)

    def is_removal(self, start: float, end: float) -> bool:
        return bool(self.ended_at) and start < self.ended_at <= end

    def is_cleared_in(self, start: float, end: float) -> bool:
        return bool(self.cleared_at) and start < self.cleared_at <= end

    def cleared(self, time: float) -> "LoadItem":
        return replace(self, cleared_at=time)

    def ended(self, time: float) -> "LoadItem":
        return replace(self, ended_at=time)

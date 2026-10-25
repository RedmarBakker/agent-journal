from dataclasses import dataclass


@dataclass(frozen=True)
class WaitProgress:
    """How far a run an agent waits on has come: when it started, the share it shows done from its percentage, its count or its step, and how long its last run took, which tell how many seconds are left."""

    started_at: float
    finished_share: float = 0.0
    last_seconds: float = 0.0

    def remaining_seconds(self, moment: float) -> float | None:
        elapsed = max(moment - self.started_at, 0.0)
        if self.finished_share > 0:
            return elapsed * (1 - self.finished_share) / self.finished_share
        return max(self.last_seconds - elapsed, 0.0) if self.last_seconds > 0 else None

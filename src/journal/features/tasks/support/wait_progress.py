from dataclasses import dataclass


@dataclass(frozen=True)
class WaitProgress:
    """How far a run an agent waits on has come: when it started, the share it shows done from its percentage, its count or its step, how long the last passing run of the same command with the same arguments took, and when it last printed; the seconds left come from that record while the run is within it, else from the share done, and are unknown with neither."""

    started_at: float
    finished_share: float = 0.0
    last_seconds: float = 0.0
    printed_at: float = 0.0

    def has_printed_since(self, moment: float) -> bool:
        return self.printed_at >= moment

    def remaining_seconds(self, moment: float) -> float | None:
        elapsed = max(moment - self.started_at, 0.0)
        if self.last_seconds > elapsed:
            return self.last_seconds - elapsed
        if self.finished_share > 0:
            return elapsed * (1 - self.finished_share) / self.finished_share
        return None

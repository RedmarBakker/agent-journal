from dataclasses import dataclass

from journal.models.support.agent_load import AgentLoad


@dataclass(frozen=True)
class QueueView:
    """One queue an agent clears as the status bar shows it: its load, what arrives and is cleared an hour, what waits and the oldest few, the minutes from arrival to clearing and Little's check of them, and the minutes it has stood high, past the scale-up level."""

    rho: float
    arrivals: float
    clearings: float
    waiting: float
    wait_minutes: float
    little: float
    waiting_refs: tuple[str, ...]
    high_minutes: float

    @classmethod
    def measured(cls, queue: AgentLoad) -> "QueueView | None":
        if not queue.is_measured():
            return None
        return cls(queue.rho, queue.arrivals, queue.clearings, queue.waiting, queue.wait_minutes, queue.little, queue.waiting_refs, queue.busy_minutes)

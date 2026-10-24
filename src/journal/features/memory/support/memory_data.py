from dataclasses import dataclass

from journal.features.memory.support.memory_row import MemoryRow
from journal.features.memory.support.timed_reminder import TimedReminder


@dataclass(frozen=True)
class MemoryData:
    """The memory feature's reading: the context mark the agent must decide at, the highest mark it has taken, every fact, rule and reminder with its keywords, the ones standing at least the set days named with their age, each with its presence in the agent's context window and its trigger, and the reminders set for a moment."""

    threshold_due: int
    context_threshold: int
    rows: tuple[MemoryRow, ...]
    stale: tuple[str, ...]
    timed: tuple[TimedReminder, ...] = ()

from dataclasses import dataclass

from journal.features.memory.support.memory_row import MemoryRow
from journal.features.memory.support.timed_reminder import TimedReminder
from journal.features.memory.support.repeating_reminder import RepeatingReminder


@dataclass(frozen=True)
class MemoryData:
    """The memory feature's reading: the context mark the agent must decide at, the highest mark it has taken, every fact, rule and reminder with keywords and not kept in the agent's context, the ones standing at least the set days named with their age, each with its presence in the agent's context window and its trigger, the reminders set for a moment, and the memories still shown as one line, heaviest first."""

    threshold_due: int
    context_threshold: int
    rows: tuple[MemoryRow, ...]
    stale: tuple[str, ...]
    timed: tuple[TimedReminder, ...] = ()
    triggered: tuple[MemoryRow, ...] = ()
    shown_memories: str = ""
    repeating: tuple[RepeatingReminder, ...] = ()

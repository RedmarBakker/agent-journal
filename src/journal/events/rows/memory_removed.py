from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class MemoryRemoved(RowEvent):
    """A memory was taken out as no longer true; it stays on its row, never shown again."""

    feature_name = "memory"

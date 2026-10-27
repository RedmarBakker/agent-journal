from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class MemoryWeighed(RowEvent):
    """A memory was given a new weight, by the agent or the user."""

    feature_name = "memory"

    weight: int

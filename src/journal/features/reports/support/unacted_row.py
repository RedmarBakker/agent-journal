from dataclasses import dataclass


@dataclass(frozen=True)
class UnactedRow:
    """A report or document never acted on: its kind as its command names it, its number and when it was written."""

    row_type: str
    row_id: int
    written_at: float

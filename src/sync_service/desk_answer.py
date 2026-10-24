from dataclasses import dataclass


@dataclass(frozen=True)
class DeskAnswer:
    """What the journal server did with an answer the sync service handed in: how many changes it applied, or that it needs the team's full copy laid in first."""

    applied: int
    needs_copy: bool

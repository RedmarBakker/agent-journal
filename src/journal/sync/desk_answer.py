from dataclasses import dataclass


@dataclass(frozen=True)
class DeskAnswer:
    """What the sync desk did with an answer from the team server: how many changes it applied, or that it needs the team's full copy laid in first, which leaves the answer to be handed again."""

    applied: int
    needs_copy: bool

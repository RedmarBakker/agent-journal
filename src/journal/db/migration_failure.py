from dataclasses import dataclass


@dataclass(frozen=True)
class MigrationFailure:
    """A migration that raised, rolled back and left unrecorded: its number, its error and the time, as a timestamp."""

    number: int
    error: str
    failed_at: float

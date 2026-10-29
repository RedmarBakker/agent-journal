from dataclasses import dataclass


@dataclass(frozen=True)
class BoardPhases:
    """The names a domain gives the four base phases of its board, the plain ones where its contract names none."""

    planned: str = "Planned"
    in_progress: str = "In progress"
    in_review: str = "In review"
    done: str = "Done"

from dataclasses import dataclass

from journal.models.board_phase import BoardPhase


@dataclass(frozen=True)
class BoardPhases:
    """The names a domain gives the four base phases of its board, the plain ones where its contract names none."""

    planned: str = "Planned"
    in_progress: str = "In progress"
    in_review: str = "In review"
    done: str = "Done"

    def name(self, phase: BoardPhase) -> str:
        return getattr(self, phase.value)

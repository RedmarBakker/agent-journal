from journal.support.card_outcome import CardOutcome
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CardProgress:
    """How far a watched run's card has come: its outcome, the reader's figure and fraction for the bar, its count of a total, how it ended, and whether its reader counts its progress, so the card keeps its bar's room from the start; the fields its card shows and a live card asks for every second."""

    outcome: CardOutcome
    figure: str
    fraction: float
    ending: str
    count: str
    counting: bool

    def fields(self) -> dict:
        return {**asdict(self), "outcome": str(self.outcome)}

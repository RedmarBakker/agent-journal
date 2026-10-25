from journal.support.card_outcome import CardOutcome
from dataclasses import dataclass


@dataclass(frozen=True)
class CardStanding:
    """A worker's status on its chat card: the words after its name, how it stands, which the viewer colours, and the line under them."""

    text: str
    outcome: CardOutcome = CardOutcome.NONE
    detail: str = ""

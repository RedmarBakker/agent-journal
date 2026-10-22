from dataclasses import dataclass


@dataclass(frozen=True)
class CardStanding:
    """A worker's status on its chat card: the words after its name, the tone they are shown in, and the line under them."""

    text: str
    tone: str = ""
    detail: str = ""

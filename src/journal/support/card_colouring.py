from enum import StrEnum


class CardColouring(StrEnum):
    """Whether a family's cards carry no colour, as events that only say something happened do, or the colour of their outcome, as processes do: blue while running, red when failed, green when passed."""

    NONE = "none"
    OUTCOME = "outcome"

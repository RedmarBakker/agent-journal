from dataclasses import dataclass

from journal.support.card_colouring import CardColouring


@dataclass(frozen=True)
class CardFamily:
    """A family of chat cards a feature declares inside a group: its title, the one icon every card of it carries, and whether its cards carry no colour or their outcome's."""

    key: str
    title: str
    icon: str
    group: str
    colouring: CardColouring = CardColouring.NONE

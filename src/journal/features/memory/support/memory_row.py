from dataclasses import dataclass

from journal.support.card_type import CardType


@dataclass(frozen=True)
class MemoryRow:
    """A rule or reminder as the feature data carries it: its noun, number, words, keywords, the chat's switch for it, its presence in the agent's context window, the trigger that brings it, whether its condition holds now, and whether it is struck once brought."""

    noun: str
    id: int
    text: str
    keywords: tuple[str, ...]
    threshold: CardType
    presence: bool = False
    trigger: str = ""
    ready: bool = False
    is_single_use: bool = False

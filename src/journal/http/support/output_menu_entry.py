from dataclasses import dataclass

from journal.chat.process_cards import DOCKED
from journal.models.command_output import CommandOutput
from journal.models.message import Message


@dataclass(frozen=True)
class OutputMenuEntry:
    """An output still running as the viewer's run menu lists it: its title, its command, when it began, its card in the chat (0 before it has one) and whether that card is docked."""

    id: int
    title: str
    command: str
    began_at: float
    card: int
    docked: bool

    @classmethod
    def build(cls, output: CommandOutput, cards: list[Message]) -> "OutputMenuEntry":
        card = cards[0] if cards else None
        title = card.text if card else output.watch_title or output.command
        return cls(output.row_id, title, output.command, output.creation_time.timestamp(), card.id if card else 0, bool(card and card.data.get(DOCKED)))

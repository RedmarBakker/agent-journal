from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.saved import Saved
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.models.command_output import CommandOutput


class OutputCard(Listener[Saved]):
    """An output moved to the background or watched is a process card in the chat, written again each time the output is saved, as it moves, is watched and ends."""

    def __init__(self, card: OutputProcessCard, cards: ProcessCards) -> None:
        self.card, self.cards = card, cards

    def handle(self, event: Saved) -> None:
        output = event.model
        if isinstance(output, CommandOutput) and (output.moved or output.is_watched):
            self.cards.show(self.card.mark(output))

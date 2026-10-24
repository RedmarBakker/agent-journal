from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.saved import Saved
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.models.command_output import CommandOutput


class OutputCard(Listener[Saved]):
    """An output moved to the background or watched is a process card in the chat, written again each time the output is saved, as it moves, is watched and ends; a run watched from its start that ends in the foreground keeps its card, turned to how it ended."""

    def __init__(self, card: OutputProcessCard, cards: ProcessCards) -> None:
        self.card, self.cards = card, cards

    def handle(self, event: Saved) -> None:
        output = event.model
        if not isinstance(output, CommandOutput):
            return
        if output.moved or output.is_watched or output.watch_reader:
            self.cards.show(self.card.card_contents(output))

from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.moments.reader_added import ReaderAdded
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.repositories.command_outputs import CommandOutputs


class ReaderOutputCards(Listener[ReaderAdded]):
    """The cards of the outputs a reader reads are written again when the reader is added or revised."""

    def __init__(self, outputs: CommandOutputs, card: OutputProcessCard, cards: ProcessCards) -> None:
        self.outputs, self.card, self.cards = outputs, card, cards

    def handle(self, event: ReaderAdded) -> None:
        for output in self.outputs.reader_outputs(event.reader):
            self.cards.show(self.card.mark(output))

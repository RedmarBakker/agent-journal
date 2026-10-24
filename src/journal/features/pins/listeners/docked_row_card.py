from journal.chat.docking import Docking
from journal.chat.process_cards import ProcessCards
from journal.chat.row_process_card import RowProcessCard
from journal.events.listener import Listener
from journal.events.moments.row_docked import RowDocked


class DockedRowCard(Listener[RowDocked]):
    """A row docked that has no card yet gets one, written for it docked."""

    def __init__(self, docking: Docking, card: RowProcessCard, cards: ProcessCards) -> None:
        self.docking, self.card, self.cards = docking, card, cards

    def handle(self, event: RowDocked) -> None:
        self.cards.show(self.card.docked_contents(event.environment_id, self.docking.table_row(event.row.type, event.row.id), event.actor))

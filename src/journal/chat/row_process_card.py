from journal.chat.process_card import ProcessCard
from journal.chat.process_cards import DOCKED
from journal.chat.process_mark import ProcessMark
from journal.models.message import Message
from journal.models.model import Model
from journal.models.support.row_card import RowCard
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class RowProcessCard(ProcessCard):
    """The process card of a row in the chat, the made card of a document or report or the card a row is docked by, which docking pins above the chat and releases."""

    name = "row"

    @staticmethod
    def key(row: Model) -> str:
        return f"made:{row.noun()}:{row.id}"

    def card_contents(self, environment_id: int, row: Model, actor: Actor) -> ProcessMark:
        data = {"kind": "made", "made_type": row.table(), "n": row.id, **RowCard.build(row).as_data()}
        return ProcessMark(self.name, environment_id, self.key(row), row.title_words(), data, actor, CardKind.CREATED, False, session=actor.id)

    def docked_contents(self, environment_id: int, row: Model, actor: Actor) -> ProcessMark:
        return ProcessMark(self.name, environment_id, self.key(row), row.heading(), {"kind": DOCKED, **RowCard.build(row).as_data()}, actor, CardKind.CREATED, False)

    def refresh(self, message: Message) -> dict:
        return {"active": False}

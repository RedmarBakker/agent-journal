from journal.chat.process_card import ProcessCard
from journal.chat.process_cards import DOCKED
from journal.chat.process_card_contents import ProcessCardContents
from journal.models.message import Message
from journal.models.model import Model
from journal.models.support.row_card import RowCard
from journal.repositories.scope import Scope
from journal.repositories.subagents import Subagents
from journal.support.actor import SUBAGENT_SEPARATOR
from journal.support.actor import Actor
from journal.support.card_type import CardType


PLAIN_NOUNS = {"doc": "document"}


class RowProcessCard(ProcessCard):
    """The process card of a row in the chat, the made card of a document, report or plan or the card a row is docked by, which docking pins above the chat and releases; a row a subagent made is shown in the chat of the agent that sent it, naming the subagent."""

    name = "row"

    def __init__(self, subagents: Subagents, scope: Scope) -> None:
        self.subagents, self.scope = subagents, scope

    @staticmethod
    def key(row: Model) -> str:
        return f"made:{row.noun()}:{row.id}"

    def card_contents(self, environment_id: int, row: Model, actor: Actor) -> ProcessCardContents:
        dispatcher, _, subagent_session = actor.id.partition(SUBAGENT_SEPARATOR)
        maker = self.subagent_label(environment_id, dispatcher, subagent_session) if actor.is_subagent() else ""
        data = {"kind": "made", "made_type": row.table(), "n": row.id, "title": row.title_words(), "maker": maker, **RowCard.build(row).as_data()}
        return ProcessCardContents(self.name, environment_id, self.key(row), self.created_line(row, maker), data, actor, CardType.CREATED, False, session=dispatcher)

    def subagent_label(self, environment_id: int, dispatcher: str, subagent_session: str) -> str:
        with self.scope.environment(environment_id):
            found = self.subagents.session_subagent(dispatcher, subagent_session)
        return f"subagent {found[0].agent_type}" if found else "a subagent"

    @staticmethod
    def created_line(row: Model, maker: str) -> str:
        title = row.title_words()
        subagent_suffix = f" by {maker}" if maker else ""
        numbered = f"Created {PLAIN_NOUNS.get(row.noun(), row.noun())} {row.id}{subagent_suffix}"
        return f"{numbered}: {title}" if title else numbered

    def docked_contents(self, environment_id: int, row: Model, actor: Actor) -> ProcessCardContents:
        return ProcessCardContents(self.name, environment_id, self.key(row), row.heading(), {"kind": DOCKED, **RowCard.build(row).as_data()}, actor, CardType.CREATED, False)

    def refresh(self, message: Message) -> dict:
        return {"active": False}

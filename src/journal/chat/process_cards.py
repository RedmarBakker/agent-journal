from journal.support.actor import Actor
from journal.chat.card_detail import CardDetail
from journal.chat.card_category import CardCategory
from journal.chat.process_card_contents import ProcessCardContents
from journal.models.author import Author
from journal.models.message import Message
from journal.models.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.repositories.messages import Messages

PROCESS = "process"
DOCKED = "docked"
AUTO_DOCKED = "auto_docked"
DOCK_TIME_KEY = "dock_at"


class ProcessCards:
    """Writes every process card: one message per process, found again by its key and updated in place, found and written in one transaction so two shows of one card at once never make two, its data naming the process card class that refreshes it and whether its process still runs."""

    def __init__(self, messages: Messages, agents: Agents) -> None:
        self.messages, self.agents = messages, agents

    def show(self, contents: ProcessCardContents) -> Message:
        data = {"row": "", **contents.data, **CardDetail.parts(contents.detail), **CardCategory.read(contents.label).fields(), "key": contents.key, "shows": str(contents.shows), "card_type": PROCESS, "process": contents.process, "active": contents.active}
        with self.messages.writing():
            older = self.messages.keyed(contents.key, contents.actor)
            if older:
                return self.messages.save(older[0].with_(text=contents.label, session=contents.session or older[0].session, data=self.docked_data(older[0], data)), contents.actor)
            roles = self.agents.session_roles(contents.session) if contents.session else []
            return self.messages.save(Message(environment_id=contents.environment_id, author=Author.SYSTEM, session=contents.session or None, agent_role=roles[0] if roles else AgentRole.MAIN, text=contents.label, data=data), contents.actor)

    def withdraw(self, key: str, actor: Actor) -> None:
        for card in self.messages.keyed(key, actor):
            self.messages.delete(card, actor)

    def show_recent(self, contents: ProcessCardContents) -> Message:
        older = self.messages.keyed(contents.key, contents.actor)
        if older and self.predates_user_message(older[0]):
            self.messages.delete(older[0], contents.actor)
        return self.show(contents)

    def predates_user_message(self, card: Message) -> bool:
        latest = self.messages.last_user_message()
        return latest is not None and card.row_id < latest.row_id

    @staticmethod
    def docked_data(older: Message, data: dict) -> dict:
        return {**{key: older.data[key] for key in (DOCKED, AUTO_DOCKED, DOCK_TIME_KEY) if key in older.data}, **data}

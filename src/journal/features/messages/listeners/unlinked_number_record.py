from functools import partial

from journal.events.listener import Listener
from journal.events.models.saved import Saved
from journal.features.messages.support.row_references import RowReferences
from journal.features.messages.support.unlinked_row_numbers import ROW_TABLES, UnlinkedRowNumbers
from journal.support.message_thread import MessageThread
from journal.models.author import Author
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.repositories.agents import Agents
from journal.repositories.messages import Messages
from journal.repositories.rows import Rows
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.listener_queue import ListenerQueue


class UnlinkedNumberRecord(Listener[Saved]):
    """Each time the main agent's chat message, never a thought, is written or edited, the numbers in it that name a row without its kind before them, each as the row it most likely is, are kept on the agent's row, and the rows it refers to with their kind that do not exist on the message itself, worked out on the deferred worker after the hook has answered, so its conduct can ask it to link them or to correct the message."""

    def __init__(self, deferred: ListenerQueue, agents: Agents, rows: Rows, scope: Scope, messages: Messages) -> None:
        self.deferred, self.agents, self.rows, self.scope, self.messages = deferred, agents, rows, scope, messages

    def handle(self, event: Saved) -> None:
        message = event.model
        if not isinstance(message, Message) or message.author != Author.AGENT or message.thread != MessageThread.MAIN or not message.session or message.is_thought:
            return
        self.deferred.add(partial(self.recorded, message))

    def recorded(self, message: Message) -> None:
        with self.scope.environment(message.environment_id):
            agents = self.agents.session_rows(message.session)
            if not agents:
                return
            row_names = tuple(f"{kind} {number}" for number in UnlinkedRowNumbers.numbers(message.text) if (kind := self.likely_kind(number)))
            if row_names or agents[0].unlinked_numbers:
                self.agents.save(agents[0].with_(unlinked_message=message.row_id, unlinked_numbers=row_names), Actor.system())
            self.store_missing_rows(message)

    def store_missing_rows(self, message: Message) -> None:
        missing = [f"{kind} {number}" for kind, number in RowReferences.rows(message.text) if not self.rows.is_row(Ref(ROW_TABLES[kind], number))]
        if missing != message.data.get(Message.MISSING_ROWS, []):
            self.messages.touched(message, Actor.system(), lambda current: {"data": {**current.data, Message.MISSING_ROWS: missing}})

    def likely_kind(self, number: int) -> str:
        return next((kind for kind, table in ROW_TABLES.items() if self.rows.is_row(Ref(table, number))), "")

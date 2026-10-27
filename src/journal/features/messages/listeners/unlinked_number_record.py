from functools import partial

from journal.events.announcer import Announcer
from journal.events.listener import Listener
from journal.events.rows.message_rows_faulty import MessageRowsFaulty
from journal.events.models.saved import Saved
from journal.features.messages.support.row_references import RowReferences
from journal.features.messages.support.unlinked_row_numbers import ROW_TABLES, UnlinkedRowNumbers
from journal.support.message_thread import MessageThread
from journal.models.author import Author
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.repositories.messages import Messages
from journal.repositories.rows import Rows
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.listener_queue import ListenerQueue


class UnlinkedNumberRecord(Listener[Saved]):
    """Each time the main agent's chat message, never a thought, is written or edited, the numbers in it that name a row without its kind before them, each as the row it most likely is, and the rows it refers to with their kind that do not exist, are worked out on the deferred worker after the hook has answered: the missing rows are kept on the message, and both are announced once for that message, so the conduct asks the agent to link them or correct it."""

    def __init__(self, deferred: ListenerQueue, rows: Rows, scope: Scope, messages: Messages, announcer: Announcer) -> None:
        self.deferred, self.rows, self.scope, self.messages, self.announcer = deferred, rows, scope, messages, announcer

    def handle(self, event: Saved) -> None:
        message = event.model
        if not isinstance(message, Message) or message.author != Author.AGENT or message.thread != MessageThread.MAIN or not message.session or message.is_thought:
            return
        self.deferred.add(partial(self.recorded, message))

    def recorded(self, message: Message) -> None:
        with self.scope.environment(message.environment_id):
            row_names = tuple(f"{kind} {number}" for number in UnlinkedRowNumbers.numbers(message.text) if (kind := self.likely_kind(number)))
            missing = [f"{kind} {number}" for kind, number in RowReferences.rows(message.text) if not self.rows.is_row(Ref(ROW_TABLES[kind], number))]
            self.store_missing_rows(message, missing)
        if row_names or missing:
            self.announcer.announce(MessageRowsFaulty(environment_id=message.environment_id, row_id=message.row_id, writer_session=message.session, unlinked=row_names, missing=tuple(missing)))

    def store_missing_rows(self, message: Message, missing: list[str]) -> None:
        if missing != message.data.get(Message.MISSING_ROWS, []):
            self.messages.touched(message, Actor.system(), lambda current: {"data": self.missing_rows_data(current.data, missing)})

    @staticmethod
    def missing_rows_data(data: dict, missing: list[str]) -> dict:
        unrelated = {key: value for key, value in data.items() if key != Message.MISSING_ROWS}
        return {**unrelated, Message.MISSING_ROWS: missing} if missing else unrelated

    def likely_kind(self, number: int) -> str:
        return next((kind for kind, table in ROW_TABLES.items() if self.rows.is_row(Ref(table, number))), "")

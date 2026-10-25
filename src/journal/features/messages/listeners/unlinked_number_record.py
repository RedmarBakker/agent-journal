from functools import partial

from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.messages.support.unlinked_row_numbers import ROW_TABLES, UnlinkedRowNumbers
from journal.models.agent_role import AgentRole
from journal.models.author import Author
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.repositories.agents import Agents
from journal.repositories.rows import Rows
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.listener_queue import ListenerQueue


class UnlinkedNumberRecord(Listener[Created]):
    """The numbers of the main agent's chat message, never a thought, that name a row without its kind before them are kept on its row, each as the row it most likely is, worked out on the deferred worker after the hook has answered, so its conduct can ask it to link them."""

    def __init__(self, deferred: ListenerQueue, agents: Agents, rows: Rows, scope: Scope) -> None:
        self.deferred, self.agents, self.rows, self.scope = deferred, agents, rows, scope

    def handle(self, event: Created) -> None:
        message = event.model
        if not isinstance(message, Message) or message.author != Author.AGENT or message.agent_role != AgentRole.MAIN or not message.session or message.is_thought:
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

    def likely_kind(self, number: int) -> str:
        return next((kind for kind, table in ROW_TABLES.items() if self.rows.is_row(Ref(table, number))), "")

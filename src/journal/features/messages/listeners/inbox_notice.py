from typing import TypeVar

from journal.engine.nudger import Nudger
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent_listener import AgentListener
from journal.support.decision import Decision
from journal.repositories.messages import Messages
from journal.features.messages.support.messages_data_reader import INBOX_LINE_IDS
from journal.features.messages.messages_nudges import MessagesNudges

E = TypeVar("E", bound=AgentEvent)


class InboxNotice(AgentListener[E]):
    """What the three moments share: what waits unread is named to the agent by number, so it reads and answers it before anything else."""

    def __init__(self, nudger: Nudger, messages: Messages) -> None:
        self.nudger, self.messages = nudger, messages

    def handle(self, event: E) -> Decision | None:
        unread = self.messages.unread_page_ids(INBOX_LINE_IDS)
        if not unread:
            return None
        line = self.nudger.deliver(event.agent, MessagesNudges.inbox(tuple(unread), self.messages.unread_count()))
        return Decision.allowed_with(line) if line else None

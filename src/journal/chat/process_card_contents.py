from dataclasses import dataclass

from journal.support.actor import Actor
from journal.support.card_type import CardType
from journal.support.message_thread import MessageThread


@dataclass(frozen=True)
class ProcessCardContents:
    """What a process card is to show now: its process, its key, its label and data, whom it is written as, whether its process still runs, and the chat thread it goes in, the agent's own when the listener that builds it holds an agent event; written by a listener through ProcessCards."""

    process: str
    environment_id: int
    key: str
    label: str
    data: dict
    actor: Actor
    shows: CardType
    active: bool
    detail: str = ""
    session: str | None = None
    thread: MessageThread = MessageThread.MAIN

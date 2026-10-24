from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class MenuAnswered(Event):
    """The journal answered a menu in an agent's terminal: its question, and what it did."""

    environment_id: int
    session: str
    question: str
    done: str

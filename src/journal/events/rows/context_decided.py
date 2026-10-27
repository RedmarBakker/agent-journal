from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ContextDecided(RowEvent):
    """An agent, named by its session, decided what to keep at a context mark: its pending mark decision is done."""

    feature_name = "memory"

    threshold: int
    agent_session: str = ""

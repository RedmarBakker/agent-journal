from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class AgentThinking(RowEvent):
    """The agent at work has been quiet long enough to be thinking, by its session."""

    agent_session: str

from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class AgentThinkingEnded(RowEvent):
    """The agent stopped thinking: a tool started, it stopped, or it went to wait, by its session."""

    feature_name = "thinking"

    agent_session: str

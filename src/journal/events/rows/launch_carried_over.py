from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class LaunchCarriedOver(RowEvent):
    """The agent's launch was carried over by a journal server on a newer version, which stopped the one on the version it had."""

    agent_session: str
    previous: str
    version: str

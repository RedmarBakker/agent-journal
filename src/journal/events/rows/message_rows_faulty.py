from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class MessageRowsFaulty(RowEvent):
    """A chat message of the agent's names rows wrongly: numbers with no kind before them, each with the kind it most likely is, or rows that do not exist; told once to the agent that wrote it."""

    feature_name = "messages"

    writer_session: str
    unlinked: tuple[str, ...]
    missing: tuple[str, ...]

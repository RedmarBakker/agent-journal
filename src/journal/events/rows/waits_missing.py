from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WaitsMissing(RowEvent):
    """Tasks were found naming another open task they do not wait on: the orchestrator's session, and each pair newly found, as task:other."""

    agent_session: str
    pairs: tuple[str, ...]

    def waits(self) -> tuple[tuple[str, ...], ...]:
        return tuple(tuple(pair.split(":")) for pair in self.pairs)

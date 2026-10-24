from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class SearchCompleted(Event):
    """Words were searched for in the rows here, and what was found."""

    environment_id: int
    session: str | None
    terms: str
    answer: str

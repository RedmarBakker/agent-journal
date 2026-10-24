from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class SlowRequestsReported(Event):
    """The agent was told of the requests that went over their budget: how many, the tally's data and its detail, at what moment."""

    environment_id: int
    total: int
    data: dict
    detail: str
    moment: float

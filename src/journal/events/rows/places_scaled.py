from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlacesScaled(RowEvent):
    """The load opened or closed a place: the orchestrator's session, the workers out at once now, the load and how many minutes it held, and whether a place opened."""

    agent_session: str
    places: int
    rho: float
    minutes: float
    opened: bool

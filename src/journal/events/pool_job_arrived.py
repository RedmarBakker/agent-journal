from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class PoolJobArrived(Event):
    """The team server offered this machine a worker from the pool, by the request's number."""

    request_id: int

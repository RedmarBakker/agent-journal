from dataclasses import dataclass


@dataclass(frozen=True)
class HostDecline:
    """A machine's word that it will not take a request up, by the request's number, and why."""

    id: int
    reason: str

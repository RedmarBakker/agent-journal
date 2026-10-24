from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class ServerReplaced(Event):
    """This journal server, once serving, stopped one of the project on an older version, whose launches it carried over."""

    previous: str
    version: str
    time: float

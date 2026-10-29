from dataclasses import dataclass
from typing import Generic, TypeVar


class Event:
    """Something that happened, dispatched to whoever hears its kind."""


E = TypeVar("E", bound=Event)


class Listener(Generic[E]):
    """Hears one kind of event."""


# @sin UnheardEventDetector
@dataclass(frozen=True)
class ParcelLoss(Event):
    parcel: int


# @righteous UnheardEventDetector
@dataclass(frozen=True)
class ParcelDispatch(Event):
    parcel: int


class DispatchNotice(Listener[ParcelDispatch]):
    """Writes the notice of a dispatched parcel."""

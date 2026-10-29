from dataclasses import dataclass
from enum import Enum


class ParcelState(Enum):
    WAITING = "waiting"
    MOVING = "moving"


class Carrier(Enum):
    POST = "post"
    COURIER = "courier"


@dataclass(frozen=True)
class Parcel:
    state: ParcelState
    carrier: Carrier

    def is_moving(self) -> bool:
        return self.state == ParcelState.MOVING

    def is_couriered(self) -> bool:
        return self.carrier == Carrier.COURIER

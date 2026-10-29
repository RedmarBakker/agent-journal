from dataclasses import dataclass

from parcel import Carrier, Parcel, ParcelState


@dataclass(frozen=True)
class Packing:
    kind: str


def routed(parcel: Parcel) -> bool:
    # @sin AnsweredFieldQuestionDetector
    return parcel.state != ParcelState.MOVING


def collected(parcel: Parcel) -> bool:
    # @sin AnsweredFieldQuestionDetector
    return parcel.carrier != Carrier.COURIER


def boxed(packing: Packing) -> bool:
    # @sin RepeatedFieldQuestionDetector
    return packing.kind == "box"


def wrapped(packing: Packing) -> bool:
    # @sin RepeatedFieldQuestionDetector
    return packing.kind != "box"


def sealed(packing: Packing) -> bool:
    # @righteous RepeatedFieldQuestionDetector
    return packing.kind == "bag"

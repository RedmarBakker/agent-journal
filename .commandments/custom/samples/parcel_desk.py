from parcel import Carrier, Parcel, ParcelState
from parcel_route import Packing


def label(parcel: Parcel) -> str:
    # @sin AnsweredFieldQuestionDetector
    return "on its way" if parcel.state == ParcelState.MOVING else "waiting"


def moving_label(parcel: Parcel) -> bool:
    # @sin AnsweredFieldQuestionDetector
    return parcel.state == ParcelState.MOVING


def priced(parcel: Parcel) -> int:
    # @sin AnsweredFieldQuestionDetector
    return 5 if parcel.carrier == Carrier.COURIER else 2


def rushed(parcel: Parcel) -> bool:
    # @sin AnsweredFieldQuestionDetector
    return parcel.carrier == Carrier.COURIER


def packed(packing: Packing) -> bool:
    # @sin RepeatedFieldQuestionDetector
    return packing.kind == "box"


def sent_check(parcel: Parcel) -> bool:
    # @righteous AnsweredFieldQuestionDetector
    return parcel.is_moving()

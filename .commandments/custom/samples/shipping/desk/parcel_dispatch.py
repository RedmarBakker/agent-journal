from dataclasses import replace

from shipping.models.parcel_record import ParcelRecord


def dispatch(record: ParcelRecord, moment: float) -> ParcelRecord:
    # @sin FieldSetOutsideItsFileDetector
    return replace(record, dispatch_time=moment)


def dispatch_plainly(record: ParcelRecord, moment: float) -> ParcelRecord:
    # @fixed FieldSetOutsideItsFileDetector
    return record.dispatched(moment)

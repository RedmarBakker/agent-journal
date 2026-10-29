from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ParcelRecord:
    weight: int
    dispatch_time: float = 0.0

    def dispatched(self, moment: float) -> "ParcelRecord":
        # @righteous FieldSetOutsideItsFileDetector
        return replace(self, dispatch_time=moment)

from dataclasses import dataclass

from tests.lab.measurement import Measurement


@dataclass(frozen=True)
class NamedMeasurement:
    name: str
    measurement: Measurement

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("a metric needs a name")

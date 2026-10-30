from tests.lab.measurement import Measurement
from tests.lab.named_measurement import NamedMeasurement


def missing_measurements(names: tuple[str, ...], reason: str, version: str) -> tuple[NamedMeasurement, ...]:
    return tuple(
        NamedMeasurement(name, Measurement(None, "missing", reason, 0, None, (), version))
        for name in names
    )


def validate_measurements(measurements: tuple[NamedMeasurement, ...], expected: tuple[str, ...], label: str) -> None:
    names = tuple(reading.name for reading in measurements)
    if names != expected:
        raise ValueError(f"{label} must include all {label} metrics exactly once in schema order")


def find_measurement(measurements: tuple[NamedMeasurement, ...], name: str) -> Measurement:
    found = next((reading.measurement for reading in measurements if reading.name == name), None)
    if found is None:
        raise KeyError(name)
    return found


def replace_measurement(
    measurements: tuple[NamedMeasurement, ...], name: str, measurement: Measurement
) -> tuple[NamedMeasurement, ...]:
    if name not in {reading.name for reading in measurements}:
        raise KeyError(name)
    return tuple(
        NamedMeasurement(reading.name, measurement if reading.name == name else reading.measurement)
        for reading in measurements
    )

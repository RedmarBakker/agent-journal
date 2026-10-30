from dataclasses import dataclass
import math
from typing import Literal


MetricStatus = Literal["observed", "partial", "missing", "not_applicable", "censored"]


@dataclass(frozen=True)
class Measurement:
    value: object
    status: MetricStatus
    reason: str
    observed_coverage: int
    expected_coverage: int | None
    source_references: tuple[str, ...]
    measurement_version: str

    def __post_init__(self) -> None:
        if self.status not in {"observed", "partial", "missing", "not_applicable", "censored"}:
            raise ValueError(f"unknown measurement status: {self.status}")
        if not self.reason.strip() or not self.measurement_version.strip():
            raise ValueError("a measurement needs a reason and version")
        if not isinstance(self.observed_coverage, int) or isinstance(self.observed_coverage, bool) or self.observed_coverage < 0:
            raise ValueError("observed coverage must be a non-negative count")
        if self.expected_coverage is not None and (
            not isinstance(self.expected_coverage, int)
            or isinstance(self.expected_coverage, bool)
            or self.expected_coverage < self.observed_coverage
        ):
            raise ValueError("expected coverage must be absent or at least the observed count")
        if self.expected_coverage is not None and self.status == "observed" and self.observed_coverage != self.expected_coverage:
            raise ValueError("observed measurements need complete expected coverage")
        if self.expected_coverage is not None and self.status == "partial" and self.observed_coverage == self.expected_coverage:
            raise ValueError("partial measurements need incomplete or unknown expected coverage")
        if not self.immutable_value(self.value):
            raise ValueError("measurement values must be finite scalars or tuples of finite values")
        if (self.status in {"missing", "not_applicable"}) != (self.value is None):
            raise ValueError("missing and not-applicable measurements have null values; other statuses retain a value")
        if any(not reference.strip() for reference in self.source_references):
            raise ValueError("source references cannot be empty")
        if len(set(self.source_references)) != len(self.source_references):
            raise ValueError("source references must be unique")

    @classmethod
    def immutable_value(cls, value: object) -> bool:
        if value is None or isinstance(value, (str, bool, int)):
            return True
        if isinstance(value, float):
            return math.isfinite(value)
        return isinstance(value, tuple) and all(cls.immutable_value(item) for item in value)

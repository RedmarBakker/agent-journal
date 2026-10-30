import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

from tests.lab.business_type import freeze


PROFILE_VERSION = "behaviour-profile-v1"
MINIMUM_OBSERVATIONS = 30
RATE_METRICS = {
    "followed_line_rate": "line_followed",
    "escalation_rate": "escalated",
    "handoff_error_rate": "handoff_error",
    "outside_route_rate": "outside_route",
    "outside_worktree_rate": "outside_worktree",
}
SAMPLE_METRICS = {"job_length_deciles_minutes": "job_length_minutes", "send_back_shares": "send_back_count", **RATE_METRICS}


@dataclass(frozen=True)
class BehaviourProfile:
    """A versioned set of sampled behaviour estimates for one agent kind and model tier."""

    agent_kind: str
    model_tier: str
    metrics: Mapping[str, Mapping[str, object]]
    version: str = PROFILE_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.agent_kind, str) or not self.agent_kind.strip() or not isinstance(self.model_tier, str) or not self.model_tier.strip() or self.version != PROFILE_VERSION:
            raise ValueError("a behaviour profile needs an agent kind, model tier and supported version")
        if set(self.metrics) != set(SAMPLE_METRICS):
            raise ValueError("behaviour profile metrics do not match its version")
        for name, metric in self.metrics.items():
            status = metric.get("status") if isinstance(metric, Mapping) else None
            if not isinstance(metric, Mapping) or not isinstance(status, str) or status not in {"calibrated", "historical_baseline", "insufficient_data", "missing"}:
                raise ValueError(f"behaviour profile metric {name} has an invalid status")
            value, count, refs, reason = metric.get("value"), metric.get("sample_count"), metric.get("source_refs"), metric.get("reason")
            if count is not None and (type(count) is not int or count < 0):
                raise ValueError(f"behaviour profile metric {name} has an invalid sample count")
            if not isinstance(refs, tuple) or any(not isinstance(ref, str) or not ref.strip() for ref in refs) or not isinstance(reason, str):
                raise ValueError(f"behaviour profile metric {name} needs source references")
            if status in {"calibrated", "historical_baseline"} and (value is None or not refs):
                raise ValueError(f"behaviour profile metric {name} needs an estimate")
            if status == "calibrated" and (count is None or count < MINIMUM_OBSERVATIONS):
                raise ValueError(f"behaviour profile metric {name} has too few real observations")
            if status in {"insufficient_data", "missing"} and value is not None:
                raise ValueError(f"behaviour profile metric {name} cannot guess an estimate")
            if status in {"calibrated", "historical_baseline"}:
                self.validate_value(name, value)
        object.__setattr__(self, "metrics", cast(Mapping[str, Mapping[str, object]], freeze(dict(self.metrics))))

    @classmethod
    def from_history(cls) -> "BehaviourProfile":
        from tests.simulation.scenarios import JOB_DECILES, SEND_BACK_SHARES

        source = ("tests/simulation/scenarios.py:9-11",)
        metrics = {
            "job_length_deciles_minutes": cls.measurement(JOB_DECILES, "historical_baseline", None, source, "Measured worker job lengths in minutes."),
            "send_back_shares": cls.measurement(SEND_BACK_SHARES, "historical_baseline", None, source, "Measured shares of work sent back once, twice and three times."),
        }
        for name in RATE_METRICS:
            metrics[name] = cls.measurement(None, "missing", None, (), "The measured-week source has no comparable observations.")
        return cls("legacy_worker", "unknown", metrics)

    @classmethod
    def fit(cls, agent_kind: str, model_tier: str, samples: Mapping[str, Sequence[object]],
            source_refs: Mapping[str, tuple[str, ...]]) -> "BehaviourProfile":
        if set(samples) - set(SAMPLE_METRICS.values()) or set(source_refs) - set(SAMPLE_METRICS.values()):
            raise ValueError("calibration samples name an unknown behaviour metric")
        metrics = {}
        for metric, raw_metric in SAMPLE_METRICS.items():
            values = samples.get(raw_metric, ())
            refs = source_refs.get(raw_metric, ())
            metrics[metric] = cls.fit_metric(metric, values, refs)
        return cls(agent_kind, model_tier, metrics)

    @classmethod
    def fit_metric(cls, metric: str, values: Sequence[object], refs: tuple[str, ...]) -> Mapping[str, object]:
        if metric not in SAMPLE_METRICS or not isinstance(values, Sequence) or isinstance(values, (str, bytes)) or not isinstance(refs, tuple) or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
            raise ValueError(f"behaviour profile metric {metric} has invalid observations")
        count = len(values)
        if count == 0:
            return cls.measurement(None, "missing", None, refs, "No comparable observations were supplied.")
        if not refs:
            raise ValueError(f"behaviour profile metric {metric} needs source references")
        if metric == "job_length_deciles_minutes":
            estimate = cls.deciles(values, metric)
        elif metric == "send_back_shares":
            estimate = cls.send_back_shares(values)
        else:
            estimate = cls.rate(values, metric)
        if count < MINIMUM_OBSERVATIONS:
            return cls.measurement(None, "insufficient_data", count, refs,
                                   f"At least {MINIMUM_OBSERVATIONS} observations are required to fit this metric.")
        return cls.measurement(estimate, "calibrated", count, refs, "Fitted from observed real-run events.")

    @staticmethod
    def measurement(value: object, status: str, count: int | None,
                    refs: tuple[str, ...], reason: str) -> Mapping[str, object]:
        return {"value": value, "status": status, "sample_count": count, "source_refs": refs, "reason": reason}

    @staticmethod
    def deciles(values: Sequence[object], metric: str) -> tuple[float, ...]:
        sample = sorted(BehaviourProfile.positive(value, metric) for value in values)
        return tuple(sample[max(0, math.ceil(percentile * len(sample)) - 1)] for percentile in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9))

    @staticmethod
    def send_back_shares(values: Sequence[object]) -> tuple[float, float, float]:
        if any(type(value) is not int or value < 0 for value in values):
            raise ValueError("send-back observations must be non-negative whole counts")
        return tuple(sum(value >= threshold for value in values) / len(values) for threshold in (1, 2, 3))

    @staticmethod
    def rate(values: Sequence[object], metric: str) -> float:
        if any(type(value) is not bool for value in values):
            raise ValueError(f"{metric} observations must be true or false")
        return sum(cast(bool, value) for value in values) / len(values)

    @staticmethod
    def positive(value: object, metric: str) -> float:
        if type(value) not in (int, float) or not math.isfinite(float(value)) or value <= 0:
            raise ValueError(f"{metric} observations must be positive finite minutes")
        return float(value)

    @staticmethod
    def validate_value(metric: str, value: object) -> None:
        if metric == "job_length_deciles_minutes":
            if not isinstance(value, tuple) or len(value) != 9 or any(type(item) not in (int, float) or not math.isfinite(item) or item <= 0 for item in value) or tuple(sorted(value)) != value:
                raise ValueError("job-length profile needs nine ordered finite minute deciles")
        elif metric == "send_back_shares":
            if not isinstance(value, tuple) or len(value) != 3 or any(type(item) not in (int, float) or not 0 <= item <= 1 for item in value) or any(left < right for left, right in zip(value, value[1:])):
                raise ValueError("send-back profile needs three descending shares between zero and one")
        elif type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{metric} profile needs a rate between zero and one")

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math

from tests.lab.metric_rule import MetricRule


@dataclass(frozen=True)
class ComparisonPlan:
    decision_rule_version: str
    metrics: tuple[MetricRule, ...]
    alpha: float
    exact_enumeration_cutoff: int
    permutation_draws: int
    bootstrap_draws: int
    random_seed: int

    def __post_init__(self) -> None:
        if not self.decision_rule_version.strip():
            raise ValueError("a comparison needs a decision-rule version")
        if sum(metric.role == "primary" for metric in self.metrics) != 1:
            raise ValueError("a comparison needs exactly one primary metric")
        if len({metric.name for metric in self.metrics}) != len(self.metrics):
            raise ValueError("comparison metric names must be unique")
        if not math.isfinite(self.alpha) or self.alpha <= 0 or self.alpha >= 1:
            raise ValueError("comparison alpha must be between zero and one")
        if self.exact_enumeration_cutoff < 1 or self.exact_enumeration_cutoff > 20 or self.permutation_draws < 1 or self.bootstrap_draws < 100:
            raise ValueError("comparison analysis needs an exact cutoff from one through twenty, positive permutation draws and at least one hundred bootstrap draws")
        if not isinstance(self.random_seed, int) or isinstance(self.random_seed, bool):
            raise ValueError("comparison randomness needs a declared integer seed")

    @property
    def digest(self) -> str:
        body = {
            "decision_rule_version": self.decision_rule_version,
            "metrics": [asdict(metric) for metric in self.metrics],
            "alpha": self.alpha,
            "exact_enumeration_cutoff": self.exact_enumeration_cutoff,
            "permutation_draws": self.permutation_draws,
            "bootstrap_draws": self.bootstrap_draws,
            "random_seed": self.random_seed,
            "sidedness": "one-sided improvement",
            "tie_handling": "inclusive extreme statistic",
            "effect_summary": "median of paired beneficial differences",
            "continuous_test_statistic": "mean of paired beneficial differences",
            "scenario_and_model_pooling": "none; report each pinned stratum",
        }
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return sha256(encoded.encode()).hexdigest()

    @property
    def primary(self) -> MetricRule:
        return next(metric for metric in self.metrics if metric.role == "primary")

from dataclasses import dataclass
import math
from typing import Literal


MetricKind = Literal["binary", "continuous"]
MetricDirection = Literal["higher", "lower"]
MetricRole = Literal["primary", "guard", "diagnostic"]
RATIO_METRICS = frozenset({
    "expectations_met_share", "critical_path_ratio", "blocked_minutes_share", "nudges_per_hour",
    "refusals_per_hour", "hops_per_handoff", "hops_per_handoff_median", "hops_per_handoff_p85",
    "handoff_rework_share", "queue_fairness_jain", "plan_message_share",
})


@dataclass(frozen=True)
class MetricRule:
    name: str
    kind: MetricKind
    direction: MetricDirection
    role: MetricRole
    practical_minimum: float | None = None
    tolerated_harm: float | None = None
    ratio_formula: str | None = None
    zero_unknown_denominator_rule: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("a comparison metric needs a name")
        if self.kind not in {"binary", "continuous"} or self.direction not in {"higher", "lower"}:
            raise ValueError("comparison metrics need a supported kind and direction")
        if self.role not in {"primary", "guard", "diagnostic"}:
            raise ValueError("comparison metrics need a supported role")
        if self.role == "primary" and (self.practical_minimum is None or not math.isfinite(self.practical_minimum) or self.practical_minimum < 0):
            raise ValueError("a primary metric needs a finite non-negative practical minimum")
        if self.role == "primary" and self.kind == "binary" and self.practical_minimum is not None and self.practical_minimum > 100:
            raise ValueError("binary practical minima are percentage points between zero and one hundred")
        if self.role != "primary" and self.practical_minimum is not None:
            raise ValueError("only the primary metric has a practical minimum")
        if self.role == "guard" and (self.tolerated_harm is None or not math.isfinite(self.tolerated_harm) or self.tolerated_harm <= 0):
            raise ValueError("a guard metric needs a finite positive tolerated-harm margin")
        if self.role != "guard" and self.tolerated_harm is not None:
            raise ValueError("only guard metrics have a tolerated-harm margin")
        has_ratio_rule = bool(self.ratio_formula and self.zero_unknown_denominator_rule)
        if self.name in RATIO_METRICS and not has_ratio_rule:
            raise ValueError("ratio metrics need a formula and zero or unknown denominator rule")
        if (self.ratio_formula is None) != (self.zero_unknown_denominator_rule is None):
            raise ValueError("ratio formula and denominator rule must be declared together")
        if self.ratio_formula is not None and (not self.ratio_formula.strip() or not self.zero_unknown_denominator_rule.strip()):
            raise ValueError("ratio formula and denominator rule must be explicit")

from dataclasses import dataclass, replace

from journal.models.model_tier import ModelTier

RIGHT, OVERPOWERED, UNDERPOWERED = "right", "too strong", "too weak"


@dataclass(frozen=True)
class ModelFit:
    """Whether the model a worker's merged work ran on fit it: how complex the work measured and the tier that complexity calls for, the tier the worker ran on, the fit the measure finds, right, too strong or too weak, empty while the worker's model is unranked, and the verdict and reason of the verifier that sampled it, empty until one did."""

    points: float = 0.0
    called_for: ModelTier = ModelTier.UNKNOWN
    tier: ModelTier = ModelTier.UNKNOWN
    measured: str = ""
    verdict: str = ""
    reason: str = ""

    @classmethod
    def parsed(cls, data: dict) -> "ModelFit":
        return cls(float(data["points"]), ModelTier(data["called_for"]), ModelTier(data["tier"]), data["measured"], data["verdict"], data["reason"])

    def judged(self, verdict: str, reason: str) -> "ModelFit":
        return replace(self, verdict=verdict, reason=reason)

    def fit(self) -> str:
        return self.verdict or self.measured

    def is_mismatch(self) -> bool:
        return self.measured in (OVERPOWERED, UNDERPOWERED)

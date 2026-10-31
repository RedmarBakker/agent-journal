from dataclasses import dataclass


@dataclass(frozen=True)
class EstimatesRiskData:
    """The current plan's forecast basis and measured scope, dependency and aging facts."""

    plan_id: int = 0
    forecast_basis: str = ""
    scope_growth_points: int = 0
    scope_growth: str = ""
    aging_task_id: int = 0
    aging_active_seconds: float = 0.0
    aging_p85_seconds: float = 0.0
    aging_samples: int = 0
    critical_prerequisites: tuple[tuple[int, int], ...] = ()
    current_sprint_end: str = ""
    sprint_probability: int | None = None
    sprint_p85: str = ""
    critical_path_advice: str = ""

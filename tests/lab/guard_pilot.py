from dataclasses import dataclass
import math


@dataclass(frozen=True)
class GuardPilot:
    metric: str
    tolerated_harm: float
    assumed_benefit: float
    seed_ids_by_scenario: tuple[tuple[str, tuple[int, ...]], ...]
    beneficial_differences_by_scenario: tuple[tuple[str, tuple[float, ...]], ...]

    def __post_init__(self) -> None:
        scenarios = tuple(name for name, _ in self.beneficial_differences_by_scenario)
        seed_scenarios = tuple(name for name, _ in self.seed_ids_by_scenario)
        if not self.metric.strip() or not scenarios or any(not name.strip() for name in scenarios) or len(set(scenarios)) != len(scenarios):
            raise ValueError("a guard pilot needs one metric and unique scenario strata")
        if not math.isfinite(self.tolerated_harm) or self.tolerated_harm <= 0:
            raise ValueError("a guard pilot needs a finite positive tolerated-harm margin")
        if not math.isfinite(self.assumed_benefit):
            raise ValueError("a guard pilot needs a finite assumed beneficial effect")
        if seed_scenarios != scenarios or any(
            len(set(seeds)) != len(seeds) or any(not isinstance(seed, int) or isinstance(seed, bool) for seed in seeds)
            for _, seeds in self.seed_ids_by_scenario
        ):
            raise ValueError("guard pilot seed IDs must be unique and match its scenario order")
        if any(not differences or any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in differences) for _, differences in self.beneficial_differences_by_scenario):
            raise ValueError("guard pilot differences must be finite paired observations")
        seeds_by_scenario = dict(self.seed_ids_by_scenario)
        differences_by_scenario = dict(self.beneficial_differences_by_scenario)
        if any(len(seeds_by_scenario[name]) != len(differences_by_scenario[name]) for name in scenarios):
            raise ValueError("every guard pilot difference needs one seed identity")

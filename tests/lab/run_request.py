from dataclasses import dataclass
from pathlib import Path

from tests.lab.design import Design
from tests.lab.scenario_pin import ScenarioPin


@dataclass(frozen=True)
class RunRequest:
    run_id: str
    attempt: int
    scenario: ScenarioPin
    design: Design
    seed: int
    provider: str
    model: str
    source_commit: str
    organization_commit: str
    metric_schema_version: str
    max_simulated_minutes: int
    root: Path
    home: Path
    result: Path

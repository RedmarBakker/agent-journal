from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re
from pathlib import Path

from tests.lab.design import Design
from tests.lab.run_request import RunRequest
from tests.lab.scenario_pin import ScenarioPin
from tests.lab.simulation_caps import SimulationCaps


@dataclass(frozen=True)
class Batch:
    batch_id: str
    scenarios: tuple[ScenarioPin, ...]
    designs: tuple[Design, ...]
    seeds: tuple[int, ...]
    source_commit: str
    organization_commit: str
    organization_version: str
    organization_checksum: str
    models: tuple[str, ...]
    caps: SimulationCaps
    metric_schema_version: str
    decision_rule_version: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[0-9a-f]{32}", self.batch_id):
            raise ValueError("batch IDs are generated opaque hexadecimal path components")
        if not self.scenarios or not self.designs or not self.seeds or not self.models:
            raise ValueError("a batch needs scenarios, designs, seeds and model tiers")
        if len({scenario.name for scenario in self.scenarios}) != len(self.scenarios):
            raise ValueError("scenario names in a batch must be unique")
        if len({design.name for design in self.designs}) != len(self.designs):
            raise ValueError("design names in a batch must be unique")
        if len(set(self.models)) != len(self.models):
            raise ValueError("model tiers in a batch must be unique")
        if any(not isinstance(seed, int) or isinstance(seed, bool) for seed in self.seeds):
            raise ValueError("batch seeds must be unique integers")
        if len(set(self.seeds)) != len(self.seeds):
            raise ValueError("batch seeds must be unique integers")
        if any(not value.strip() for value in (self.source_commit, self.organization_commit, self.organization_version, self.metric_schema_version, self.decision_rule_version, *self.models)):
            raise ValueError("a batch needs source, organization, model and rule pins")
        if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", self.source_commit):
            raise ValueError("the journal source pin must be a full commit hash")
        if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", self.organization_commit):
            raise ValueError("the organization commit pin must be a full commit hash")
        if not re.fullmatch(r"[0-9a-f]{64}", self.organization_checksum):
            raise ValueError("the organization pin needs its full SHA-256 checksum")
        if self.run_count > self.caps.max_runs:
            raise ValueError("the batch exceeds its declared run cap")
        if any(scenario.simulated_minutes > self.caps.max_simulated_minutes for scenario in self.scenarios):
            raise ValueError("a scenario exceeds the declared simulated-minute cap")

    @property
    def run_count(self) -> int:
        return len(self.scenarios) * len(self.designs) * len(self.models) * len(self.seeds)

    @classmethod
    def from_mapping(cls, recipe: dict[str, object]) -> "Batch":
        return cls(
            str(recipe["batch_id"]),
            tuple(ScenarioPin(str(row["name"]), str(row["business_type"]), str(row["version"]), str(row["checksum"]), row["simulated_minutes"]) for row in recipe["scenarios"]),
            tuple(Design.from_mapping(str(row["name"]), row["settings"]) for row in recipe["designs"]),
            tuple(recipe["seeds"]),
            str(recipe["source_commit"]),
            str(recipe["organization_commit"]),
            str(recipe["organization_version"]),
            str(recipe["organization_checksum"]),
            tuple(str(model) for model in recipe["models"]),
            SimulationCaps(**recipe["caps"]),
            str(recipe["metric_schema_version"]),
            str(recipe["decision_rule_version"]),
        )

    def requests(self, lab_home: Path) -> tuple[RunRequest, ...]:
        requests = []
        for index, (scenario, design, model, seed) in enumerate(
            ((scenario, design, model, seed) for scenario in self.scenarios for design in self.designs for model in self.models for seed in self.seeds),
            start=1,
        ):
            run_id = sha256(f"{self.batch_id}:{index}".encode()).hexdigest()[:32]
            requests.append(RunRequest(
                run_id, 1, scenario, design, seed, "VoidProvider", model, self.source_commit,
                self.organization_commit, self.metric_schema_version, self.caps.max_simulated_minutes,
                lab_home / "roots" / self.batch_id / run_id,
                lab_home / "homes" / self.batch_id / run_id,
                lab_home / "batches" / self.batch_id / "runs" / run_id / "result.json",
            ))
        return tuple(requests)

    def manifest(self, lab_home: Path) -> dict[str, object]:
        requests = self.requests(lab_home)
        body = {
            "schema_version": 1,
            "batch_id": self.batch_id,
            "mode": "simulated",
            "scenarios": [asdict(scenario) for scenario in self.scenarios],
            "designs": [design.manifest() for design in self.designs],
            "seeds": list(self.seeds),
            "runs": [
                {"run_id": request.run_id, "attempt": request.attempt, "scenario": request.scenario.name,
                 "design": request.design.name, "seed": request.seed, "provider": request.provider, "model": request.model}
                for request in requests
            ],
            "source_commit": self.source_commit,
            "organization": {"commit": self.organization_commit, "version": self.organization_version, "checksum": self.organization_checksum},
            "providers": ["VoidProvider"],
            "models": list(self.models),
            "root_map": {
                request.run_id: {"root": str(request.root), "home": str(request.home), "result": str(request.result)}
                for request in requests
            },
            "metric_schema_version": self.metric_schema_version,
            "decision_rule_version": self.decision_rule_version,
            "caps": asdict(self.caps),
            "approval_scope": [],
        }
        digest = sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        return {**body, "content_digest": digest}

    @staticmethod
    def canonical(manifest: dict[str, object]) -> str:
        return json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"

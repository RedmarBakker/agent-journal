from hashlib import sha256
import json
from pathlib import Path

from tests.lab.batch import Batch
from tests.lab.batch_runner import BatchRunner
from tests.lab.network_reading import NETWORK_METRICS
from tests.lab.null_trial_runner import run_one as simulator_run_one
from tests.lab.simulation_caps import SimulationCaps
from tests.lab.trial_brief import RULE_VERSION, TrialBrief, first_trial_briefs


METRIC_SCHEMA_VERSION = "first-trial-null-simulator-v1"
NULL_MODEL_SCOPE = (
    "deterministic paired null replay validates pinned pairing, metric adapters and zero-cost records; "
    "it does not execute agent work, apply candidate settings or estimate treatment effects"
)


def batches(source_commit: str) -> tuple[tuple[TrialBrief, Batch], ...]:
    if len(source_commit) not in {40, 64} or any(character not in "0123456789abcdef" for character in source_commit):
        raise ValueError("simulator source pin must be a full lowercase commit hash")
    return tuple((trial, batch(trial, source_commit)) for trial in first_trial_briefs())


def batch(trial, source_commit: str) -> Batch:
    designs = trial.setting.designs("A", "B", {})
    manifest = trial.manifest()
    max_minutes = max(scenario.simulated_minutes for scenario in trial.scenarios)
    return Batch(
        sha256(f"task-204:{trial.trial_id}:{manifest['decision_rule_digest']}".encode()).hexdigest()[:32],
        trial.scenarios,
        designs,
        (20401, 20402, 20403),
        source_commit,
        source_commit,
        "built-in-business-specs-v1",
        organization_checksum(trial.scenarios),
        (simulator_model(),),
        SimulationCaps(20, 1, 1_000_000, 300.0, 30.0, max_minutes),
        METRIC_SCHEMA_VERSION,
        RULE_VERSION,
        manifest["decision_rule_digest"],
    )


def run(lab_home: Path, source_commit: str) -> tuple[Path, ...]:
    generated = []
    batch_runner = BatchRunner(simulator_run_one, lab_home, workers=1)
    for trial, planned in batches(source_commit):
        result_path = batch_runner.run(planned)
        summary_path = result_path.with_name("trial-summary.json")
        batch_runner.atomic_write(summary_path, summary(trial, planned, lab_home, result_path))
        generated.append(summary_path)
    return tuple(generated)


def simulator_model() -> str:
    root = Path(__file__).parent
    repository = root.parents[1]
    paths = (
        root / "first_trial_simulation.py",
        root / "null_trial_runner.py",
        root / "trial_brief.py",
        root / "trial_setting.py",
        repository / "src" / "journal" / "features" / "workers" / "organization_options.py",
        root / "network_reading.py",
        root / "measurement.py",
        root / "run_reading.py",
    )
    digest = sha256()
    for path in paths:
        digest.update(path.relative_to(repository).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"paired-null-v1:{digest.hexdigest()}"


def organization_checksum(scenarios) -> str:
    root = Path(__file__).parent
    paths = [root / "organization_template" / name for name in ("domain.md", "role.md")]
    paths.extend(root / "business_types" / f"{scenario.business_type}.toml" for scenario in scenarios)
    digest = sha256()
    for path in sorted(set(paths)):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def summary(trial, planned: Batch, lab_home: Path, results: Path) -> str:
    records = tuple(json.loads(line) for line in results.read_text(encoding="utf-8").splitlines())
    by_key = {
        (record["scenario"], record["seed"], record["design_digest"]): record
        for record in records
    }
    scenario_results = []
    for scenario in planned.scenarios:
        pairs = []
        for seed in planned.seeds:
            a = by_key[(scenario.name, seed, planned.designs[0].digest)]
            b = by_key[(scenario.name, seed, planned.designs[1].digest)]
            a_value, a_status = metric(a, trial.primary.name)
            b_value, b_status = metric(b, trial.primary.name)
            if a_value != b_value or a_status != b_status or a_status != "observed":
                raise ValueError("the null simulator must replay identical paired readings")
            pairs.append({"seed": seed, "a": a_value, "b": b_value, "status": a_status})
        scenario_results.append({
            "business_type": scenario.business_type,
            "scenario": scenario.name,
            "paired_units": len(pairs),
            "primary_pairs_replayed_equal": len(pairs),
            "primary_metric": trial.primary.name,
            "pairs": pairs,
        })
    body = {
        "mode": "simulated_only",
        "simulation_model": planned.models[0],
        "model_scope": NULL_MODEL_SCOPE,
        "trial": trial.manifest(),
        "batch_manifest": str(lab_home / "batches" / planned.batch_id / "manifest.json"),
        "run_records": str(results),
        "run_count": len(records),
        "paired_units": trial.paired_units,
        "per_business_type": scenario_results,
        "decision": "inconclusive",
        "decision_reason": "null-model replays validate the dry-run path only; real comparisons require an approved real batch",
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def metric(record: dict, name: str) -> tuple[object, str]:
    section = "network" if name in NETWORK_METRICS else "reading"
    found = next(item["measurement"] for item in record[section]["measurements"] if item["name"] == name)
    return found["value"], found["status"]


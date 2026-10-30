from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
import stat
from typing import Any

from tests.lab.batch import Batch
from tests.lab.batch_runner import BatchRunner
from tests.lab.lab_report import LabReport
from tests.lab.measurement import Measurement
from tests.lab.network_reading import NETWORK_METRICS
from tests.lab.run_reading import RUN_METRICS


@dataclass(frozen=True)
class DriftReport:
    lab_home: Path
    baseline_batch_id: str
    current_batch: Batch

    def __post_init__(self) -> None:
        if not self.lab_home.is_absolute():
            raise ValueError("a drift report needs an absolute lab home")
        if not re.fullmatch(r"[0-9a-f]{32}", self.baseline_batch_id):
            raise ValueError("the baseline batch ID must be an opaque hexadecimal path component")
        if self.baseline_batch_id == self.current_batch.batch_id:
            raise ValueError("a regression batch needs a different baseline batch")

    @property
    def report_path(self) -> Path:
        return self.lab_home / "batches" / self.current_batch.batch_id / "report.md"

    def validate(self) -> None:
        baseline = self.read_manifest(self.baseline_batch_id)
        current = self.current_batch.manifest(self.lab_home)
        self.validate_pins(baseline, current)
        self.read_records(self.baseline_batch_id, baseline)

    def write(self) -> Path:
        baseline = self.read_manifest(self.baseline_batch_id)
        current = self.read_manifest(self.current_batch.batch_id)
        if current != self.current_batch.manifest(self.lab_home):
            raise ValueError("the scheduled regression manifest differs from its pinned recipe")
        self.validate_pins(baseline, current)
        baseline_records = self.read_records(self.baseline_batch_id, baseline)
        current_records = self.read_records(self.current_batch.batch_id, current)
        if baseline_records.keys() != current_records.keys():
            raise ValueError("regression run identities differ from the pinned baseline")
        result = self.compare(baseline, current, baseline_records, current_records)
        return LabReport.write_content(self.report_path, self.render(result))

    def read_manifest(self, batch_id: str) -> dict[str, Any]:
        folder = self.batch_folder(batch_id)
        path = folder / "manifest.json"
        if path.is_symlink() or not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise ValueError(f"batch {batch_id} has no regular manifest")
        value = json.loads(path.read_text())
        if not isinstance(value, dict) or value.get("batch_id") != batch_id:
            raise ValueError(f"batch {batch_id} has an invalid manifest")
        body = {key: item for key, item in value.items() if key != "content_digest"}
        if value.get("content_digest") != Batch.content_digest(body):
            raise ValueError(f"batch {batch_id} manifest digest does not match its contents")
        return value

    def read_records(self, batch_id: str, manifest: dict[str, Any]) -> dict[tuple[str, str, str, int], dict[str, Any]]:
        path = self.batch_folder(batch_id) / "runs.jsonl"
        if path.is_symlink() or not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise ValueError(f"batch {batch_id} has no regular run ledger")
        scenarios = {row["name"]: row for row in manifest["scenarios"]}
        designs = {row["name"]: row for row in manifest["designs"]}
        expected = {}
        for run in manifest["runs"]:
            key = (run["scenario"], run["design"], run["model"], run["seed"])
            if run["run_id"] in expected or key in expected.values():
                raise ValueError(f"batch {batch_id} has duplicate planned run identities")
            expected[run["run_id"]] = key
        records = {}
        for line in path.read_text().splitlines():
            record = json.loads(line)
            run_id = record.get("run_id")
            key = expected.get(run_id)
            if key is None or key in records:
                raise ValueError(f"batch {batch_id} has an unknown or duplicate run result")
            scenario_name, design_name, model, seed = key
            scenario = scenarios[scenario_name]
            design = designs[design_name]
            identity = (
                record.get("attempt"), record.get("scenario"), record.get("scenario_version"),
                record.get("business_type"), record.get("design_digest"), record.get("settings_digest"),
                record.get("seed"), record.get("journal_commit"), record.get("organization_commit"),
                record.get("provider"), record.get("model"), record.get("simulated"),
                record.get("metric_schema_version"),
            )
            pinned = (
                1, scenario_name, scenario["version"], scenario["business_type"], design["digest"],
                design["settings_digest"], seed, manifest["source_commit"], manifest["organization"]["commit"],
                "VoidProvider", model, True, manifest["metric_schema_version"],
            )
            if identity != pinned:
                raise ValueError(f"batch {batch_id} run {run_id} differs from its manifest")
            if record.get("terminal_reason") not in {"completed", "capped", "setup_failed", "faulted", "aborted"}:
                raise ValueError(f"batch {batch_id} run {run_id} has an invalid terminal reason")
            BatchRunner.metric_names(record, "reading", RUN_METRICS)
            BatchRunner.metric_names(record, "network", NETWORK_METRICS)
            self.validate_measurements(record, "reading", manifest["metric_schema_version"])
            self.validate_measurements(record, "network", manifest["metric_schema_version"])
            records[key] = record
        if records.keys() != set(expected.values()):
            raise ValueError(f"batch {batch_id} does not contain every planned run result")
        return records

    @staticmethod
    def validate_pins(baseline: dict[str, Any], current: dict[str, Any]) -> None:
        if baseline.get("mode") != "simulated" or current.get("mode") != "simulated":
            raise ValueError("scheduled drift reports compare simulated batches only")
        if baseline.get("providers") != ["VoidProvider"] or current.get("providers") != ["VoidProvider"]:
            raise ValueError("scheduled drift reports require VoidProvider batches")
        if baseline.get("approval_scope") != [] or current.get("approval_scope") != []:
            raise ValueError("scheduled drift reports cannot include real-run approvals")
        for name in (
            "schema_version", "scenarios", "designs", "seeds", "providers", "models",
            "metric_schema_version", "decision_rule_version", "decision_rule_digest", "caps", "approval_scope",
        ):
            if baseline.get(name) != current.get(name):
                raise ValueError(f"scheduled regression must keep pinned {name} unchanged")

    @staticmethod
    def validate_measurements(record: dict[str, Any], section: str, version: str) -> None:
        for item in record[section]["measurements"]:
            row = item["measurement"]
            measurement = Measurement(
                DriftReport.decode_value(row["value"]), row["status"], row["reason"],
                row["observed_coverage"], row["expected_coverage"],
                tuple(row["source_references"]), row["measurement_version"],
            )
            if measurement.measurement_version != version:
                raise ValueError(f"{section} measurement differs from the pinned metric schema")

    @staticmethod
    def decode_value(value: Any) -> Any:
        return tuple(value) if isinstance(value, list) else value

    @staticmethod
    def compare(
        baseline: dict[str, Any],
        current: dict[str, Any],
        baseline_records: dict[tuple[str, str, str, int], dict[str, Any]],
        current_records: dict[tuple[str, str, str, int], dict[str, Any]],
    ) -> dict[str, Any]:
        groups: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
        for key, before in baseline_records.items():
            scenario, design, model, seed = key
            after = current_records[key]
            for section, names in (("reading", RUN_METRICS), ("network", NETWORK_METRICS)):
                before_values = {item["name"]: item["measurement"] for item in before[section]["measurements"]}
                after_values = {item["name"]: item["measurement"] for item in after[section]["measurements"]}
                for name in names:
                    group_key = (section, name, scenario, design, model)
                    group = groups.setdefault(group_key, {
                        "pairs": 0, "changed": [], "incomplete": [], "incomplete_reasons": Counter(),
                        "baseline_statuses": Counter(), "current_statuses": Counter(),
                    })
                    left, right = before_values[name], after_values[name]
                    group["pairs"] += 1
                    group["baseline_statuses"][left["status"]] += 1
                    group["current_statuses"][right["status"]] += 1
                    if left["status"] != "observed" or right["status"] != "observed":
                        group["incomplete"].append(seed)
                        if left["status"] != "observed":
                            group["incomplete_reasons"][("baseline", left["status"], left["reason"])] += 1
                        if right["status"] != "observed":
                            group["incomplete_reasons"][("current", right["status"], right["reason"])] += 1
                    if DriftReport.measurement_signature(left) != DriftReport.measurement_signature(right):
                        group["changed"].append({
                            "seed": seed,
                            "baseline": DriftReport.measurement_evidence(left),
                            "current": DriftReport.measurement_evidence(right),
                        })
        strata = []
        for (section, metric, scenario, design, model), group in sorted(groups.items()):
            status = "drift_observed" if group["changed"] else "inconclusive" if group["incomplete"] else "no_drift_observed"
            strata.append({
                "section": section, "metric": metric, "scenario": scenario, "design": design, "model": model,
                "pairs": group["pairs"], "changed_pairs": len(group["changed"]),
                "incomplete_pairs": len(group["incomplete"]), "status": status,
                "baseline_statuses": dict(sorted(group["baseline_statuses"].items())),
                "current_statuses": dict(sorted(group["current_statuses"].items())),
                "incomplete_seeds": sorted(group["incomplete"]), "changes": group["changed"],
                "incomplete_reasons": [
                    {"batch": side, "status": measurement_status, "reason": reason, "count": count}
                    for (side, measurement_status, reason), count in sorted(group["incomplete_reasons"].items())
                ],
            })
        return {
            "baseline": DriftReport.batch_summary(baseline, baseline_records),
            "current": DriftReport.batch_summary(current, current_records),
            "strata": strata,
            "drift_count": sum(row["status"] == "drift_observed" for row in strata),
            "inconclusive_count": sum(row["status"] == "inconclusive" for row in strata),
            "unchanged_count": sum(row["status"] == "no_drift_observed" for row in strata),
        }

    @staticmethod
    def measurement_signature(value: dict[str, Any]) -> tuple[Any, ...]:
        return value["status"], DriftReport.decode_value(value["value"]), value["observed_coverage"], value["expected_coverage"]

    @staticmethod
    def measurement_evidence(value: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": value["status"], "value": DriftReport.decode_value(value["value"]),
            "observed_coverage": value["observed_coverage"], "expected_coverage": value["expected_coverage"],
            "reason": value["reason"], "source_references": value["source_references"],
        }

    @staticmethod
    def batch_summary(manifest: dict[str, Any], records: dict[tuple[str, str, str, int], dict[str, Any]]) -> dict[str, Any]:
        terminal_reasons = Counter(record["terminal_reason"] for record in records.values())
        resources = []
        setup_failures = []
        resource_names = ("cost_units", "cost_dollars", "agent_turns", "tool_uses")
        for key, record in sorted(records.items()):
            run_metrics = {item["name"]: item["measurement"] for item in record["reading"]["measurements"]}
            resources.append({
                "run_id": record["run_id"], "scenario": key[0], "design": key[1], "model": key[2],
                "seed": key[3], "terminal_reason": record["terminal_reason"],
                "setup_minutes": DriftReport.measurement_evidence(record["setup_minutes"]),
                "usage": {name: DriftReport.measurement_evidence(run_metrics[name]) for name in resource_names},
            })
            if record["terminal_reason"] != "completed":
                setup_failures.append({
                    "run_id": record["run_id"], "terminal_reason": record["terminal_reason"],
                    "setup_diagnostics": record["reading"]["setup_diagnostics"],
                })
        return {
            "batch_id": manifest["batch_id"], "manifest_digest": manifest["content_digest"],
            "source_commit": manifest["source_commit"], "organization_commit": manifest["organization"]["commit"],
            "manifest_path": f"batches/{manifest['batch_id']}/manifest.json",
            "runs_path": f"batches/{manifest['batch_id']}/runs.jsonl",
            "run_count": len(records), "terminal_reasons": dict(sorted(terminal_reasons.items())),
            "seeds": manifest["seeds"], "caps": manifest["caps"],
            "resources": resources, "setup_failures": setup_failures,
        }

    @staticmethod
    def render(result: dict[str, Any]) -> str:
        if result["drift_count"]:
            summary = (
                f"Observed exact metric changes in {result['drift_count']} strata; "
                f"{result['inconclusive_count']} strata remain inconclusive. Treat all changes as exploratory drift."
            )
        elif result["inconclusive_count"]:
            summary = f"No changes were observed in complete strata; {result['inconclusive_count']} strata remain inconclusive."
        else:
            summary = "No metric changes were observed in the complete simulated sample."
        lines = [
            "# Scheduled regression drift report", "", "## Summary", "", summary,
            "", "This report compares one simulated batch with a pinned simulated baseline.",
            "The external scheduler owns the cadence; this command does not schedule another run.",
            "", "## Batch pins", "", "```json", LabReport._json({"baseline": result["baseline"], "current": result["current"]}), "```",
            "", "## Metric drift", "", "| Metric | Scenario | Design | Model | Pairs | Changed | Incomplete | Status |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
        for row in result["strata"]:
            lines.append("| " + " | ".join((
                *(LabReport._cell(row[key]) for key in ("metric", "scenario", "design", "model")), str(row["pairs"]),
                str(row["changed_pairs"]), str(row["incomplete_pairs"]), row["status"],
            )) + " |")
        changed = [row for row in result["strata"] if row["changes"]]
        incomplete = [
            {key: row[key] for key in ("section", "metric", "scenario", "design", "model", "incomplete_pairs", "incomplete_reasons")}
            for row in result["strata"] if row["incomplete_pairs"]
        ]
        lines.extend((
            "", "## Changed measurements", "", "```json", LabReport._json(changed), "```",
            "", "## Incomplete evidence", "", "```json", LabReport._json(incomplete), "```",
            "", "## Limits", "",
            "A difference is a drift signal, not a statistical keep/drop decision. Missing, partial or censored readings remain incomplete; they are never treated as zero.",
            "This report is exploratory evidence for a new task. It causes no automatic setting change or rollback, task filing or real-provider spend.",
            "Source and organization pins identify the compared software; if both change, this report does not attribute drift to either one.",
            "The manifests and runs.jsonl files in both batch directories retain every assigned seed, cap and run result.",
        ))
        return "\n".join(lines) + "\n"

    def batch_folder(self, batch_id: str) -> Path:
        batches = self.lab_home / "batches"
        folder = batches / batch_id
        if (
            self.lab_home.is_symlink() or batches.is_symlink() or folder.is_symlink()
            or not self.lab_home.is_dir() or not batches.is_dir() or not folder.is_dir()
        ):
            raise ValueError(f"batch {batch_id} is not stored in a private lab batch directory")
        if any(stat.S_IMODE(path.stat().st_mode) & 0o077 for path in (self.lab_home, batches, folder)):
            raise ValueError(f"batch {batch_id} is not stored in private lab directories")
        if folder.resolve().parent != batches.resolve():
            raise ValueError(f"batch {batch_id} resolves outside the lab batch directory")
        return folder

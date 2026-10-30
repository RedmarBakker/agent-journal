from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from tests.lab.batch import Batch
from tests.lab.comparison_plan import ComparisonPlan
from tests.lab.network_reading import NETWORK_METRICS
from tests.lab.paired_tests import PairedTests
from tests.lab.run_reading import RUN_METRICS
from tests.lab.run_record import RunRecord


@dataclass(frozen=True)
class Comparison:
    batch: Batch
    lab_home: Path
    records: tuple[RunRecord, ...]
    plan: ComparisonPlan

    def __post_init__(self) -> None:
        if not self.lab_home.is_absolute():
            raise ValueError("a comparison needs the batch's absolute lab home")
        if len(self.batch.designs) != 2:
            raise ValueError("a paired comparison needs exactly two pinned designs, A then B")
        if self.plan.decision_rule_version != self.batch.decision_rule_version or self.plan.digest != self.batch.decision_rule_digest:
            raise ValueError("comparison decision rules differ from the frozen batch manifest")
        if any(metric.name not in {*RUN_METRICS, *NETWORK_METRICS} for metric in self.plan.metrics):
            raise ValueError("comparison metrics must belong to a pinned run or network schema")
        requests = {request.run_id: request for request in self.batch.requests(self.lab_home)}
        found = set()
        for record in self.records:
            request = requests.get(record.run_id)
            if request is None or record.run_id in found:
                raise ValueError("comparison records must have unique run IDs from the frozen batch")
            found.add(record.run_id)
            if (
                record.attempt != request.attempt
                or record.scenario != request.scenario.name
                or record.scenario_version != request.scenario.version
                or record.business_type != request.scenario.business_type
                or record.design_digest != request.design.digest
                or record.settings_digest != request.design.settings_digest
                or record.seed != request.seed
                or record.journal_commit != request.source_commit
                or record.organization_commit != request.organization_commit
                or record.provider != request.provider
                or record.model != request.model
                or record.metric_schema_version != request.metric_schema_version
                or record.simulated is not True
            ):
                raise ValueError("comparison run evidence differs from its pinned batch request")

    @property
    def manifest_digest(self) -> str:
        return str(self.batch.manifest(self.lab_home)["content_digest"])

    @property
    def report_path(self) -> Path:
        return self.lab_home / "batches" / self.batch.batch_id / "report.md"

    def analyze(self) -> dict[str, Any]:
        requests = self.batch.requests(self.lab_home)
        request_by_key = {
            (request.scenario.name, request.model, request.seed, request.design.name): request
            for request in requests
        }
        records_by_id = {record.run_id: record for record in self.records}
        group_results = []
        confirmatory_members = []
        for metric in self.plan.metrics:
            for scenario in self.batch.scenarios:
                for model in self.batch.models:
                    key = f"{metric.name}|{scenario.business_type}|{scenario.name}|{model}"
                    a_values = []
                    b_values = []
                    a_terminal_reasons = []
                    b_terminal_reasons = []
                    missing_pair_reasons = []
                    for seed in self.batch.seeds:
                        a_request = request_by_key[(scenario.name, model, seed, self.batch.designs[0].name)]
                        b_request = request_by_key[(scenario.name, model, seed, self.batch.designs[1].name)]
                        a_record = records_by_id.get(a_request.run_id)
                        b_record = records_by_id.get(b_request.run_id)
                        a_value, a_reason = self._metric_value(a_record, metric.name, metric.kind)
                        b_value, b_reason = self._metric_value(b_record, metric.name, metric.kind)
                        a_values.append(a_value)
                        b_values.append(b_value)
                        if a_reason:
                            missing_pair_reasons.append({"seed": seed, "design": "A", "reason": a_reason})
                        if b_reason:
                            missing_pair_reasons.append({"seed": seed, "design": "B", "reason": b_reason})
                        a_terminal_reasons.append(a_record.terminal_reason if a_record else "missing_record")
                        b_terminal_reasons.append(b_record.terminal_reason if b_record else "missing_record")
                    if metric.kind == "binary" and metric.role != "guard":
                        a_success = tuple(self._oriented_binary(value, metric.direction) for value in a_values)
                        b_success = tuple(self._oriented_binary(value, metric.direction) for value in b_values)
                        analysis = PairedTests.mcnemar(a_success, b_success)
                    elif metric.kind == "continuous":
                        differences = tuple(self._benefit_difference(a, b, metric.direction) for a, b in zip(a_values, b_values))
                        analysis = PairedTests.continuous(
                            differences,
                            random_seed=self._group_seed(key),
                            permutation_draws=self.plan.permutation_draws,
                            exact_enumeration_cutoff=self.plan.exact_enumeration_cutoff,
                            bootstrap_draws=self.plan.bootstrap_draws,
                            independent_unit="paired seed within one scenario and model",
                            null_value=-float(metric.tolerated_harm) if metric.role == "guard" else 0.0,
                        )
                    else:
                        analysis = {
                            "method": "unsupported binary non-inferiority method",
                            "status": "unready",
                            "assumption": "no binary guard margin test is selected by this plan",
                            "pair_count": len(self.batch.seeds),
                            "missing_pair_count": len(self.batch.seeds),
                            "p_value": None,
                        }
                    result = {
                        "family_member": key,
                        "metric": metric.name,
                        "role": metric.role,
                        "business_type": scenario.business_type,
                        "scenario": scenario.name,
                        "model": model,
                        "terminal_reasons": {
                            "A": self._reason_counts(a_terminal_reasons),
                            "B": self._reason_counts(b_terminal_reasons),
                        },
                        "missing_pair_reasons": missing_pair_reasons,
                        "analysis": analysis,
                    }
                    group_results.append(result)
                    if metric.role in {"primary", "guard"}:
                        confirmatory_members.append((key, analysis.get("p_value")))
        correction = PairedTests.holm(confirmatory_members, self.plan.alpha) if confirmatory_members else {
            "method": "Holm step-down familywise correction", "alpha": self.plan.alpha, "family_size": 0, "members": {},
        }
        for result in group_results:
            member = correction["members"].get(result["family_member"])
            result["holm"] = member
        decision, reason = self._decision(group_results, correction)
        return {
            "batch_id": self.batch.batch_id,
            "mode": "simulated",
            "manifest_digest": self.manifest_digest,
            "decision_rule_version": self.plan.decision_rule_version,
            "decision_rule_digest": self.plan.digest,
            "design_a": self.batch.designs[0].name,
            "design_b": self.batch.designs[1].name,
            "confirmatory_family": correction,
            "metric_rules": [asdict(metric) for metric in self.plan.metrics],
            "results": group_results,
            "recommendation": decision,
            "recommendation_reason": reason,
            "action_taken": False,
        }

    def _decision(self, results: list[dict[str, Any]], correction: dict[str, Any]) -> tuple[str, str]:
        family = correction["members"]
        if any(member["p_value"] is None or not member["passed"] for member in family.values()):
            return "inconclusive", "every frozen primary and guard test must be present and pass Holm correction before B is eligible"
        primary = self.plan.primary
        primary_results = [result for result in results if result["metric"] == primary.name]
        if any(result["analysis"].get("missing_pair_count", 0) for result in primary_results):
            return "inconclusive", "missing paired readings cannot support a keep recommendation"
        for result in primary_results:
            analysis = result["analysis"]
            effect = analysis.get("effect_percentage_points") if primary.kind == "binary" else analysis.get("effect_median")
            if effect is None or effect < float(primary.practical_minimum):
                return "inconclusive", "the primary point improvement does not meet its preregistered practical minimum"
        return "keep_eligible", "the primary improvement and every frozen guard pass their preregistered thresholds"

    @staticmethod
    def _metric_value(record: RunRecord | None, name: str, kind: str) -> tuple[object | None, str | None]:
        if record is None:
            return None, "run result is missing from the frozen batch"
        reading = record.reading if name in RUN_METRICS else record.network
        measurement = reading.measurement(name)
        if measurement.status != "observed":
            return None, f"{measurement.status}: {measurement.reason}"
        if record.terminal_reason != "completed" and name != "goal_reached":
            return None, f"terminal reason {record.terminal_reason} makes this metric incomplete at cutoff"
        if kind == "binary" and not isinstance(measurement.value, bool):
            return None, "observed metric value is not boolean"
        if kind == "continuous" and (isinstance(measurement.value, bool) or not isinstance(measurement.value, (int, float))):
            return None, "observed metric value is not numeric"
        return measurement.value, None

    @staticmethod
    def _reason_counts(reasons: list[str]) -> dict[str, int]:
        return dict(sorted(Counter(reasons).items()))

    @staticmethod
    def _oriented_binary(value: object | None, direction: str) -> bool | None:
        if value is None:
            return None
        if not isinstance(value, bool):
            return None
        return value if direction == "higher" else not value

    @staticmethod
    def _benefit_difference(a: object | None, b: object | None, direction: str) -> float | None:
        if a is None or b is None:
            return None
        if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return None
        return float(b - a if direction == "higher" else a - b)

    def _group_seed(self, key: str) -> int:
        seed_digest = sha256(f"{self.plan.random_seed}:{key}".encode()).digest()
        return int.from_bytes(seed_digest[:8], "big")

import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any

from tests.lab.comparison import Comparison
from tests.lab.seed_estimate import SeedEstimate


class LabReport:
    @staticmethod
    def draft(comparison: Comparison, seed_estimate: SeedEstimate | None = None) -> dict[str, str]:
        result = comparison.analyze()
        abstract = LabReport._abstract(result)
        sections = [
            "## Summary",
            "",
            abstract,
            "",
            "## Trial and pins",
            "",
            "```json",
            LabReport._json({
                "batch_id": result["batch_id"],
                "mode": result["mode"],
                "manifest_digest": result["manifest_digest"],
                "decision_rule_version": result["decision_rule_version"],
                "decision_rule_digest": result["decision_rule_digest"],
                "design_a": result["design_a"],
                "design_b": result["design_b"],
                "pins": result["pins"],
            }),
            "```",
            "",
            "## Recommendation",
            "",
            f"- Recommendation: {result['recommendation']}",
            f"- Reason: {result['recommendation_reason']}",
            "- Action taken: no",
            "",
            "## Results",
            "",
            LabReport._results_table(result),
            "",
            "## Confirmatory family",
            "",
            "```json",
            LabReport._json(result["confirmatory_family"]),
            "```",
            "",
            "## Evidence and methods",
            "",
            "```json",
            LabReport._json({"metric_rules": result["metric_rules"], "results": result["results"]}),
            "```",
            "",
        ]
        if seed_estimate is not None:
            sections.extend(("## Seed estimate", "", "```json", LabReport._json(seed_estimate.manifest()), "```", ""))
        sections.extend((
            "## Limits",
            "",
            "This is simulated benchmark evidence only; it does not establish production effectiveness.",
            "Filing a journal report is an explicit operator action.",
        ))
        return {
            "title": f"Lab comparison {result['batch_id']}",
            "abstract": abstract,
            "body": "\n".join(sections) + "\n",
        }

    @staticmethod
    def render(comparison: Comparison, seed_estimate: SeedEstimate | None = None) -> str:
        return LabReport.draft(comparison, seed_estimate)["body"]

    @staticmethod
    def write(comparison: Comparison, seed_estimate: SeedEstimate | None = None) -> Path:
        destination = comparison.report_path
        parent = destination.parent
        if not parent.is_dir() or parent.is_symlink() or stat.S_IMODE(parent.stat().st_mode) & 0o077:
            raise ValueError("the report batch directory must already exist and be private")
        descriptor, temporary = tempfile.mkstemp(prefix=".report-", dir=parent)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w") as report:
                report.write(LabReport.render(comparison, seed_estimate))
                report.flush()
                os.fsync(report.fileno())
            os.replace(temporary, destination)
        except BaseException:
            os.unlink(temporary)
            raise
        return destination

    @staticmethod
    def _abstract(result: dict[str, Any]) -> str:
        if result["recommendation"] == "keep_eligible":
            return "B is eligible for operator review under the simulated comparison; no setting changed."
        return "The simulated comparison is inconclusive; no setting changed."

    @staticmethod
    def _results_table(result: dict[str, Any]) -> str:
        lines = [
            "| Metric | Business type | Scenario | Model | Effect | Raw p | Holm p | Status |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
        for row in result["results"]:
            analysis = row["analysis"]
            effect = analysis.get("effect_percentage_points", analysis.get("effect_median"))
            holm = row.get("holm") or {}
            lines.append("| " + " | ".join((
                LabReport._cell(row["metric"]), LabReport._cell(row["business_type"]),
                LabReport._cell(row["scenario"]), LabReport._cell(row["model"]),
                LabReport._format(effect), LabReport._format(analysis.get("p_value")),
                LabReport._format(holm.get("adjusted_p_value")), LabReport._cell(analysis.get("status", "unavailable")),
            )) + " |")
        return "\n".join(lines)

    @staticmethod
    def _json(value: object) -> str:
        return json.dumps(value, sort_keys=True, indent=2, allow_nan=False)

    @staticmethod
    def _format(value: Any) -> str:
        if value is None:
            return "not available"
        return f"{value:.6g}" if isinstance(value, (int, float)) else str(value)

    @staticmethod
    def _cell(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

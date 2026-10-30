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
    def render(comparison: Comparison, seed_estimate: SeedEstimate | None = None) -> str:
        result = comparison.analyze()
        lines = [
            "# Lab comparison",
            "",
            f"- Batch: `{result['batch_id']}`",
            f"- Mode: `{result['mode']}`",
            f"- Manifest digest: `{result['manifest_digest']}`",
            f"- Decision-rule version: `{result['decision_rule_version']}`",
            f"- Decision-rule digest: `{result['decision_rule_digest']}`",
            f"- Designs: `{result['design_a']}` (A) and `{result['design_b']}` (B)",
            f"- Recommendation: **{result['recommendation']}** — {result['recommendation_reason']}",
            "- Action taken: no",
            "",
            "## Confirmatory results",
            "",
            "| Metric | Business type | Scenario | Model | Method | Effect | Raw p | Holm p | Status |",
            "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
        for row in result["results"]:
            analysis = row["analysis"]
            effect = analysis.get("effect_percentage_points", analysis.get("effect_median"))
            holm = row.get("holm") or {}
            lines.append(
                "| " + " | ".join((
                    str(row["metric"]), str(row["business_type"]), str(row["scenario"]), str(row["model"]),
                    LabReport._cell(analysis.get("method", "unavailable")), LabReport._format(effect),
                    LabReport._format(analysis.get("p_value")), LabReport._format(holm.get("adjusted_p_value")),
                    LabReport._cell(analysis.get("status", "unavailable")),
                )) + " |"
            )
        lines.extend(("", "## Analysis family", "", "```json", json.dumps(result["confirmatory_family"], sort_keys=True, indent=2), "```", ""))
        lines.extend(("## Metric rules and paired evidence", "", "```json", json.dumps({"metric_rules": result["metric_rules"], "results": result["results"]}, sort_keys=True, indent=2), "```", ""))
        if seed_estimate is not None:
            lines.extend(("## Seed estimate", "", "```json", json.dumps(seed_estimate.manifest(), sort_keys=True, indent=2), "```", ""))
        lines.append("This is simulated benchmark evidence only; it does not establish production effectiveness.")
        lines.append("Filing a journal report is an explicit operator action.")
        return "\n".join(lines) + "\n"

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
    def _format(value: Any) -> str:
        if value is None:
            return "not available"
        return f"{value:.6g}" if isinstance(value, (int, float)) else str(value)

    @staticmethod
    def _cell(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

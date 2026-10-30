from dataclasses import dataclass
from datetime import datetime

from tests.lab.measurement import Measurement
from tests.lab.named_measurement import NamedMeasurement
from tests.lab.reading_support import find_measurement, missing_measurements, replace_measurement, validate_measurements
from tests.lab.setup_diagnostic import SetupDiagnostic


RUN_METRICS = (
    "goal_reached",
    "expectations_met_share",
    "work_on_main",
    "approvals_respected",
    "writes_outside_worktree",
    "judge_score",
    "minutes_to_done",
    "critical_path_ratio",
    "cost_units",
    "cost_dollars",
    "agent_turns",
    "tool_uses",
    "send_backs",
    "short_proofs",
    "reopened_tasks",
    "wait_releases",
    "blocks_count",
    "blocked_minutes_share",
    "longest_wait_minutes",
    "idle_seat_minutes",
    "nudges_per_hour",
    "refusals_per_hour",
    "invariants_broken",
    "faults",
)

SETUP_CHECKS = (
    "first_commit",
    "branch_guard_worktree_ordering",
    "supervisor_reachable",
    "sanitized_launch_environment",
    "absolute_private_shim",
    "assigned_write_root_coverage",
    "required_artifacts_on_main",
    "usage_coverage",
)


@dataclass(frozen=True)
class RunReading:
    measurements: tuple[NamedMeasurement, ...]
    setup_diagnostics: tuple[SetupDiagnostic, ...]

    def __post_init__(self) -> None:
        validate_measurements(self.measurements, RUN_METRICS, "run")
        names = tuple(diagnostic.name for diagnostic in self.setup_diagnostics)
        if names != SETUP_CHECKS:
            raise ValueError("run setup diagnostics must include every setup check exactly once in schema order")

    @classmethod
    def missing(cls, reason: str, version: str) -> "RunReading":
        diagnostics = tuple(
            SetupDiagnostic(name, "unknown", None, reason, ())
            for name in SETUP_CHECKS
        )
        return cls(missing_measurements(RUN_METRICS, reason, version), diagnostics)

    def measurement(self, name: str) -> Measurement:
        return find_measurement(self.measurements, name)

    def with_measurement(self, name: str, measurement: Measurement) -> "RunReading":
        return RunReading(replace_measurement(self.measurements, name, measurement), self.setup_diagnostics)

    def with_setup_diagnostic(self, diagnostic: SetupDiagnostic) -> "RunReading":
        if diagnostic.name not in SETUP_CHECKS:
            raise KeyError(diagnostic.name)
        diagnostics = tuple(
            diagnostic if current.name == diagnostic.name else current
            for current in self.setup_diagnostics
        )
        return RunReading(self.measurements, diagnostics)

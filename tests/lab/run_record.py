from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
from typing import Literal

from tests.lab.measurement import Measurement
from tests.lab.network_reading import NetworkReading
from tests.lab.run_reading import RunReading


TerminalReason = Literal["completed", "capped", "setup_failed", "faulted", "aborted"]


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    attempt: int
    scenario: str
    scenario_version: str
    business_type: str
    design_digest: str
    settings_digest: str
    seed: int
    journal_commit: str
    organization_commit: str
    provider: str
    model: str
    simulated: bool
    metric_schema_version: str
    observation_started_at: datetime
    observation_ended_at: datetime
    terminal_reason: TerminalReason
    setup_minutes: Measurement
    reading: RunReading
    network: NetworkReading

    def __post_init__(self) -> None:
        identifiers = (
            self.run_id, self.scenario, self.scenario_version, self.business_type,
            self.design_digest, self.settings_digest, self.journal_commit,
            self.organization_commit, self.provider, self.model, self.metric_schema_version,
        )
        if any(not value.strip() for value in identifiers):
            raise ValueError("a run record needs every run, scenario, design, commit, provider and schema identity")
        if self.attempt < 1:
            raise ValueError("run attempts start at one")
        if self.terminal_reason not in {"completed", "capped", "setup_failed", "faulted", "aborted"}:
            raise ValueError(f"unknown run terminal reason: {self.terminal_reason}")
        if self.observation_started_at.utcoffset() != timedelta(0) or self.observation_ended_at.utcoffset() != timedelta(0):
            raise ValueError("run evidence timestamps must be UTC")
        if self.observation_ended_at < self.observation_started_at:
            raise ValueError("run observation end must not precede its start")
        if self.terminal_reason == "setup_failed" and self.reading.measurement("minutes_to_done").status != "not_applicable":
            raise ValueError("a failed setup has no work window")

    def json_line(self) -> str:
        return json.dumps(asdict(self), default=self.json_value, sort_keys=True, separators=(",", ":"), allow_nan=False)

    @staticmethod
    def json_value(value: object) -> str:
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        raise TypeError(f"cannot serialize {type(value).__name__} in a run record")

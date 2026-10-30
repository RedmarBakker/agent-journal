import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RunRecord:
    """The immutable outcome and isolation evidence for one real run attempt."""

    run_id: str
    attempt: int
    scenario: str
    business_type: str
    design_digest: str
    seed: int
    manifest_digest: str
    journal_commit: str
    organization_commit: str
    provider: str
    model: str
    metric_schema_version: str
    terminal_reason: str
    setup_seconds: float
    launch_id: str = ""
    journal_pid: int | None = None
    isolation_verified: bool = False
    denied_write_count: int = 0
    escaped_write_count: int = 0
    started_at: str = ""
    ended_at: str = ""
    observation_started_at: str = ""
    observation_ended_at: str = ""
    plan_commits_reached_main: bool | None = None
    outside_worktree_changes: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        text_fields = (self.run_id, self.scenario, self.business_type, self.design_digest, self.manifest_digest, self.launch_id,
                       self.journal_commit, self.organization_commit, self.provider, self.model,
                       self.metric_schema_version, self.started_at, self.ended_at,
                       self.observation_started_at, self.observation_ended_at)
        if self.terminal_reason not in {"completed", "capped", "setup_failed", "faulted", "aborted"}:
            raise ValueError(f"unknown real-run terminal reason: {self.terminal_reason}")
        if any(not isinstance(value, str) for value in text_fields):
            raise ValueError("run record text fields must be strings")
        if type(self.attempt) is not int or self.attempt < 1 or type(self.seed) is not int:
            raise ValueError("run attempts start at one and scenario seeds must be whole numbers")
        if type(self.setup_seconds) not in (int, float) or not math.isfinite(self.setup_seconds) or self.setup_seconds < 0:
            raise ValueError("run attempts start at one and setup time cannot be negative")
        if self.plan_commits_reached_main is not None and type(self.plan_commits_reached_main) is not bool:
            raise ValueError("main-merge evidence must be true, false or unknown")
        if self.journal_pid is not None and (type(self.journal_pid) is not int or self.journal_pid <= 0):
            raise ValueError("journal endpoint process id must be positive when known")
        if type(self.isolation_verified) is not bool:
            raise ValueError("isolation verification must be recorded as true or false")
        if type(self.denied_write_count) is not int or self.denied_write_count < 0 or type(self.escaped_write_count) is not int or self.escaped_write_count < 0:
            raise ValueError("isolation write counts must be non-negative whole numbers")
        if any(not isinstance(value, str) for value in (*self.outside_worktree_changes, *self.evidence)):
            raise ValueError("run record changes and evidence must be text")

    def to_document(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "attempt": self.attempt,
            "scenario": self.scenario,
            "business_type": self.business_type,
            "design_digest": self.design_digest,
            "seed": self.seed,
            "manifest_digest": self.manifest_digest,
            "journal_commit": self.journal_commit,
            "organization_commit": self.organization_commit,
            "provider": self.provider,
            "model": self.model,
            "metric_schema_version": self.metric_schema_version,
            "terminal_reason": self.terminal_reason,
            "setup_seconds": self.setup_seconds,
            "launch_id": self.launch_id,
            "journal_pid": self.journal_pid,
            "isolation_verified": self.isolation_verified,
            "denied_write_count": self.denied_write_count,
            "escaped_write_count": self.escaped_write_count,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "observation_started_at": self.observation_started_at,
            "observation_ended_at": self.observation_ended_at,
            "plan_commits_reached_main": self.plan_commits_reached_main,
            "outside_worktree_changes": list(self.outside_worktree_changes),
            "evidence": list(self.evidence),
        }

    @classmethod
    def from_document(cls, document: dict[str, object]) -> "RunRecord":
        expected = {
            "run_id", "attempt", "scenario", "business_type", "design_digest", "seed", "manifest_digest",
            "journal_commit", "organization_commit", "provider", "model", "metric_schema_version",
            "terminal_reason", "setup_seconds", "launch_id", "journal_pid", "isolation_verified",
            "denied_write_count", "escaped_write_count",
            "started_at", "ended_at", "observation_started_at",
            "observation_ended_at", "plan_commits_reached_main", "outside_worktree_changes", "evidence",
        }
        if set(document) != expected:
            raise ValueError("run record fields do not match the immutable record schema")
        for key in ("outside_worktree_changes", "evidence"):
            value = document[key]
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise ValueError(f"run record {key} must be a list of strings")
        return cls(**{**document, "outside_worktree_changes": tuple(document["outside_worktree_changes"]),
                      "evidence": tuple(document["evidence"])})

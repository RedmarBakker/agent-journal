from pathlib import Path
from time import monotonic, time
from typing import Callable

from journal.support.actor import Actor
from tests.lab.real.batch_approval import BatchApproval
from tests.lab.real.isolated_journal import IsolatedJournal
from tests.lab.real.manifest import Manifest
from tests.lab.real.real_run import RealRun
from tests.lab.real.run_caps import RunCaps
from tests.lab.real.run_record import RunRecord
from tests.lab.real.run_record_store import RunRecordStore


class RunRealBatch:
    """Preflight an approved batch before running each pinned entry in its own isolated journal."""

    def __init__(self, approvals: BatchApproval, journal: IsolatedJournal, driver_factory: Callable,
                 boundary_factory: Callable, records: RunRecordStore, ledger: Path, watchdog: object,
                 clock: Callable[[], float] = monotonic, wall_clock: Callable[[], float] = time) -> None:
        if not hasattr(watchdog, "arm") or not hasattr(watchdog, "stop"):
            raise ValueError("a batch-owned watchdog with arm and stop is required")
        self.approvals, self.journal, self.driver_factory = approvals, journal, driver_factory
        self.boundary_factory, self.records, self.ledger = boundary_factory, records, ledger
        self.watchdog = watchdog
        self.clock, self.wall_clock = clock, wall_clock

    def run(self, manifest: Manifest, receipt, actor: Actor) -> tuple[RunRecord, ...]:
        data = manifest.data()
        run_ids = self.preflight(manifest, receipt, actor, data)
        records = []
        try:
            for run_id in run_ids:
                spec = RealRun.run_spec(data, run_id)
                driver = self.driver_factory(run_id, spec)
                caps = RunCaps(run_id, data["run_caps"][run_id], data["batch_caps"], self.ledger,
                               self.watchdog, self.clock, str(data.get("billing_mode", "metered")))
                boundary = self.boundary_factory(run_id)
                result = RealRun(self.journal, self.approvals, driver, self.records).run(
                    manifest, receipt, actor, run_id, 1, caps, boundary,
                )
                self.persist_fallback_record(manifest.batch_id, run_id, result)
                records.append(result)
                ledger = caps.read()
                if result.terminal_reason in {"setup_failed", "faulted", "aborted"} or ledger.get("quarantined"):
                    break
        finally:
            if self.watchdog.stop(f"batch:{self.ledger.parent.name}", "batch execution finished") is not True:
                raise ValueError("batch watchdog stop was not confirmed")
        return tuple(records)

    def record_path(self, batch_id: str, run_id: str) -> Path:
        root = self.journal.run_root(batch_id, run_id)
        if root.exists():
            return root / "evidence" / "run-record.json"
        return self.fallback_evidence(run_id) / "run-record.json"

    def persist_fallback_record(self, batch_id: str, run_id: str, record: RunRecord) -> None:
        root = self.journal.run_root(batch_id, run_id)
        if root.exists():
            return
        evidence = self.fallback_evidence(run_id)
        if evidence.exists() or evidence.is_symlink():
            raise ValueError("run record fallback cannot reuse an earlier attempt")
        directory = evidence.parent.parent
        for path in (directory, evidence.parent, evidence):
            if path.is_symlink():
                raise ValueError("run record fallback cannot use a symlink path")
            path.mkdir(mode=0o700, exist_ok=True)
            if path.stat().st_mode & 0o077:
                raise ValueError("run record fallback directories must be private")
        self.records.write(evidence, record)

    def fallback_evidence(self, run_id: str) -> Path:
        return self.ledger.parent / "records" / run_id / "evidence"

    def preflight(self, manifest: Manifest, receipt, actor: Actor, data: dict[str, object]) -> tuple[str, ...]:
        if receipt is None:
            raise ValueError("the owner batch approval receipt is missing")
        self.approvals.validate_caps(data)
        self.approvals.validate_providers(data)
        run_ids = self.approvals.run_ids(data)
        for run_id in run_ids:
            spec = RealRun.run_spec(data, run_id)
            attempts = spec.get("attempts", [1])
            if not isinstance(attempts, list) or attempts != [1]:
                raise ValueError("a real batch run must select one first attempt before execution")
            self.approvals.verify(manifest, receipt, run_id, actor, self.wall_clock())
            if self.journal.run_root(manifest.batch_id, run_id).exists() or self.fallback_evidence(run_id).exists():
                raise ValueError(f"run {run_id} already has an isolated root; an approved batch cannot be replayed")
        return run_ids

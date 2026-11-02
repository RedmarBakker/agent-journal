from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import secrets
from time import monotonic
from typing import Mapping

from journal.support.actor import Actor
from tests.lab.real.batch_approval import BatchApproval
from tests.lab.real.isolated_journal import IsolatedJournal
from tests.lab.real.isolation_evidence import IsolationEvidence
from tests.lab.real.manifest import Manifest
from tests.lab.real.run_caps import RunCaps
from tests.lab.real.run_record import RunRecord
from tests.lab.real.run_record_store import RunRecordStore


class RealRun:
    """Admit one approved scenario, run it through an owned driver and persist its journal record."""

    def __init__(self, journal: IsolatedJournal, approvals: BatchApproval, driver: object,
                 records: RunRecordStore) -> None:
        self.journal, self.approvals, self.driver, self.records = journal, approvals, driver, records

    def run(self, manifest: Manifest, receipt, actor: Actor, run_id: str, attempt: int,
            caps: RunCaps, boundary: object | None) -> RunRecord:
        if type(attempt) is not int or attempt < 1:
            raise ValueError("real-run attempts start at one")
        start = monotonic()
        started_at = datetime.now(timezone.utc).isoformat()
        paths: Mapping[str, object] = {}
        spec: Mapping[str, object] = {}
        try:
            data = manifest.data()
            spec = self.run_spec(data, run_id)
            self.approvals.verify(manifest, receipt, run_id, actor, datetime.now(timezone.utc).timestamp())
            self.validate_caps(data, run_id, caps)
            subscription_provider = spec["provider"] if data.get("billing_mode", "metered") == "subscription" else None
            paths = self.journal.prepare(manifest.batch_id, run_id, boundary, subscription_provider)
            if caps.ledger.resolve().is_relative_to(paths["project"].resolve()):
                raise ValueError("reservation ledger cannot be writable by the run agent")
            caps.reserve_run()
            caps.arm_watchdog()
        except (KeyError, OSError, TypeError, ValueError) as error:
            isolation, isolation_fault = (None, "")
            if paths and boundary is not None:
                isolation, isolation_fault = self.observe_isolation(boundary, run_id, paths, caps)
                error = ValueError(self.add_fault(str(error), isolation_fault)) if isolation_fault else error
            try:
                caps.cancel_before_launch()
            except Exception as cleanup_error:
                error = ValueError(self.add_fault(str(error), f"admission cleanup failed: {cleanup_error}"))
            record = self.setup_failure(manifest, spec, run_id, attempt, start, str(error), paths,
                                        denied_writes=isolation.denied_writes if isolation else 0,
                                        escaped_writes=isolation.escaped_writes if isolation else 0)
            return self.persist_record(manifest, run_id, record, paths)

        plan_id = None
        before: tuple[str, ...] = ()
        fault = ""
        launch_id = secrets.token_hex(16)
        challenge = secrets.token_hex(32)
        journal_pid = None
        try:
            _snapshot, identity, scenario = self.prepare_journal(spec, paths, run_id, launch_id, challenge, caps)
            journal_pid = identity["pid"]
            before = tuple(self.driver.outside_worktree_changes(paths))
            plan_id = self.driver.start_plan(scenario, paths, caps)
            terminal_reason = self.driver.wait_for_end_or_cap(run_id, plan_id, caps)
        except Exception as error:
            terminal_reason = "setup_failed" if plan_id is None else "faulted"
            fault = str(error)
        isolation, isolation_fault = self.observe_isolation(boundary, run_id, paths, caps)
        if isolation_fault:
            terminal_reason = "faulted"
            fault = self.add_fault(fault, isolation_fault)
        stop_confirmed = self.stop_owned(run_id)
        try:
            caps.finish_run(stop_confirmed)
        except Exception as error:
            stop_confirmed = False
            fault = self.add_fault(fault, f"cap ledger finalization failed: {error}")
        if not stop_confirmed:
            terminal_reason = "faulted"
            fault = self.add_fault(fault, "owned process stop was not confirmed")
        if plan_id is None:
            record = self.setup_failure(manifest, spec, run_id, attempt, start, fault or "plan did not start", paths,
                                        launch_id, journal_pid, journal_pid is not None,
                                        isolation.denied_writes if isolation else 0,
                                        isolation.escaped_writes if isolation else 0)
            return self.persist_record(manifest, run_id, record, paths)
        record = self.completed_record(manifest, spec, run_id, attempt, start, started_at, terminal_reason,
                                        plan_id, before, paths, fault, launch_id, journal_pid)
        record = replace(record, denied_write_count=isolation.denied_writes if isolation else 0,
                         escaped_write_count=isolation.escaped_writes if isolation else 0,
                         isolation_verified=journal_pid is not None and isolation is not None and isolation.escaped_writes == 0)
        return self.persist_record(manifest, run_id, record, paths)

    def prepare_journal(self, spec: Mapping[str, object], paths: Mapping[str, Path], run_id: str,
                        launch_id: str, challenge: str, caps) -> tuple[
                            Mapping[str, object], Mapping[str, object], object,
                        ]:
        snapshot = self.driver.materialize_project(spec, paths)
        port = self.snapshot_port(snapshot, spec)
        shim = self.journal.install_journal_shim(paths, port)
        identity = self.driver.start_journal(paths, shim, run_id, launch_id, challenge, port, caps)
        IsolatedJournal.verify_identity(identity, paths["root"], run_id, launch_id, challenge, port)
        scenario = self.driver.load_scenario(spec["scenario"], paths)
        return snapshot, identity, scenario

    def completed_record(self, manifest: Manifest, spec: Mapping[str, object], run_id: str, attempt: int,
                         start: float, started_at: str, terminal_reason: str, plan_id: object,
                         before: tuple[str, ...], paths: Mapping[str, object], fault: str,
                         launch_id: str, journal_pid: int | None) -> RunRecord:
        try:
            record = self.driver.read_record(run_id)
            if not isinstance(record, RunRecord) or record.run_id != run_id or record.manifest_digest != manifest.digest:
                raise ValueError("isolated journal returned a run record for a different run or manifest")
            outside = tuple(sorted(set(self.driver.outside_worktree_changes(paths)) - set(before)))
            reached_main = self.driver.plan_commits_reached_main(plan_id, paths)
        except Exception as error:
            fault = self.add_fault(fault, f"run record could not be verified: {error}")
            record = self.setup_failure(manifest, spec, run_id, attempt, start, fault, paths,
                                        launch_id, journal_pid, journal_pid is not None)
            terminal_reason = "faulted"
            outside = ()
            reached_main = None
        return replace(record, terminal_reason=terminal_reason, setup_seconds=max(0.0, monotonic() - start),
                       launch_id=launch_id, journal_pid=journal_pid, isolation_verified=journal_pid is not None,
                       started_at=record.started_at or started_at, ended_at=datetime.now(timezone.utc).isoformat(),
                       plan_commits_reached_main=reached_main, outside_worktree_changes=outside,
                       evidence=(*record.evidence, *((fault,) if fault else ())))

    def setup_only(self, manifest: Manifest, receipt, actor: Actor, run_id: str,
                   boundary: object | None) -> tuple[bool, Path]:
        start = monotonic()
        data = manifest.data()
        spec: Mapping[str, object] = {}
        paths: Mapping[str, Path] = {}
        setup: dict[str, object] = {}
        fault = ""
        try:
            spec = self.run_spec(data, run_id)
            self.approvals.verify(manifest, receipt, run_id, actor, datetime.now(timezone.utc).timestamp())
            subscription_provider = spec["provider"] if data.get("billing_mode", "metered") == "subscription" else None
            paths = self.journal.prepare(manifest.batch_id, run_id, boundary, subscription_provider)
            launch_id, challenge = secrets.token_hex(16), secrets.token_hex(32)
            snapshot, identity, scenario = self.prepare_journal(spec, paths, run_id, launch_id, challenge, None)
            port = identity["port"]
            plan_id = self.driver.prepare_plan(scenario, paths)
            agent_cli_probe = self.driver.probe_agent_cli(paths)
            setup = {
                "run_id": run_id,
                "status": "ready",
                "journal_commit": snapshot["journal_commit"],
                "organization_commit": snapshot["organization_commit"],
                "scenario": spec["scenario"],
                "journal_pid": identity["pid"],
                "journal_port": port,
                "plan_id": plan_id,
                "agent_cli_probe": agent_cli_probe,
                "agent_started": False,
                "provider_started": False,
            }
        except Exception as error:
            fault = str(error)

        if not paths:
            root = self.journal.run_root(manifest.batch_id, run_id)
            if root.exists():
                paths = self.journal.paths(root)
        isolation = None
        if paths and (paths["evidence"] / "isolation-start.json").is_file():
            try:
                isolation = self.journal.observe_boundary(boundary, run_id, paths)
                if isolation.escaped_writes:
                    fault = self.add_fault(fault, f"isolation observer recorded {isolation.escaped_writes} escaped writes")
            except Exception as error:
                fault = self.add_fault(fault, f"isolation observer did not confirm setup: {error}")
        if self.stop_owned(run_id) is not True:
            fault = self.add_fault(fault, "setup-only could not confirm its owned journal process stopped")
        if fault:
            if paths:
                failure = paths["evidence"] / "setup-failed.json"
                if not failure.exists():
                    self.journal.setup_failed(paths, run_id, fault)
                return False, failure
            raise ValueError(fault)
        if isolation is None:
            raise ValueError("setup-only isolation evidence is missing")
        setup["isolation_observation"] = isolation.to_document()
        setup["setup_seconds"] = max(0.0, monotonic() - start)
        return True, self.journal.write_document(paths, "setup-only.json", setup)

    def persist_record(self, manifest: Manifest, run_id: str, record: RunRecord,
                       paths: Mapping[str, object]) -> RunRecord:
        evidence = paths.get("evidence")
        if isinstance(evidence, Path) and evidence.is_dir():
            self.records.write(evidence, record)
            return record
        try:
            root = self.journal.run_root(manifest.batch_id, run_id)
        except ValueError:
            return record
        evidence = root / "evidence"
        if evidence.is_dir():
            self.records.write(evidence, record)
        return record

    @staticmethod
    def validate_caps(data: Mapping[str, object], run_id: str, caps: RunCaps) -> None:
        run_caps = data.get("run_caps")
        batch_caps = data.get("batch_caps")
        if not isinstance(run_caps, Mapping) or not isinstance(batch_caps, Mapping) or run_id not in run_caps:
            raise ValueError("manifest must contain this run's selected caps")
        if caps.run_id != run_id or caps.run_caps != run_caps[run_id] or caps.batch_caps != batch_caps:
            raise ValueError("run caps do not match the approved manifest")
        if caps.billing_mode != data.get("billing_mode", "metered"):
            raise ValueError("run billing mode does not match the approved manifest")

    @staticmethod
    def snapshot_port(snapshot: object, spec: Mapping[str, object]) -> int:
        if not isinstance(snapshot, Mapping):
            raise ValueError("isolated project snapshot must attest its selected journal revisions and private port")
        if snapshot.get("journal_commit") != spec["journal_commit"] or snapshot.get("organization_commit") != spec["organization_commit"]:
            raise ValueError("isolated project snapshot does not match the approved journal and organization commits")
        port = snapshot.get("journal_port")
        if type(port) is not int or not 1 <= port <= 65535:
            raise ValueError("isolated project snapshot needs a private loopback journal port")
        return port

    def stop_owned(self, run_id: str) -> bool:
        try:
            return self.driver.stop_owned(run_id) is True
        except Exception:
            return False

    def observe_isolation(self, boundary: object, run_id: str, paths: Mapping[str, object],
                          caps: RunCaps) -> tuple[IsolationEvidence | None, str]:
        try:
            evidence = self.journal.observe_boundary(boundary, run_id, paths)
        except Exception as error:
            reason = f"isolation observer did not confirm the run boundary: {error}"
            caps.quarantine(reason)
            return None, reason
        if evidence.escaped_writes:
            reason = f"isolation observer recorded {evidence.escaped_writes} escaped writes"
            caps.quarantine(reason)
            return evidence, reason
        return evidence, ""

    @staticmethod
    def run_spec(data: Mapping[str, object], run_id: str) -> Mapping[str, object]:
        runs = data.get("runs")
        if not isinstance(runs, list):
            raise ValueError("batch manifest must list its admitted runs")
        spec = next((item for item in runs if isinstance(item, Mapping) and item.get("id") == run_id), None)
        if spec is None:
            raise ValueError("run id is not in the batch manifest")
        required = ("scenario", "business_type", "design_digest", "journal_commit", "organization_commit",
                    "provider", "model", "metric_schema_version")
        if any(not isinstance(spec.get(key), str) or not spec[key] for key in required) or type(spec.get("seed")) is not int:
            raise ValueError("run manifest must identify its scenario, revisions, provider, model and integer seed")
        return spec

    @staticmethod
    def setup_failure(manifest: Manifest, spec: Mapping[str, object], run_id: str, attempt: int,
                      start: float, reason: str, paths: Mapping[str, object], launch_id: str = "",
                      journal_pid: int | None = None, isolation_verified: bool = False,
                      denied_writes: int = 0, escaped_writes: int = 0) -> RunRecord:
        if paths and "evidence" in paths:
            IsolatedJournal.setup_failed(paths, run_id, reason)
        return RunRecord(run_id=run_id, attempt=attempt, scenario=str(spec.get("scenario", "")),
                         business_type=str(spec.get("business_type", "")), design_digest=str(spec.get("design_digest", "")),
                         seed=int(spec.get("seed", 0)), manifest_digest=manifest.digest,
                         journal_commit=str(spec.get("journal_commit", "")), organization_commit=str(spec.get("organization_commit", "")),
                         provider=str(spec.get("provider", "")), model=str(spec.get("model", "")),
                         metric_schema_version=str(spec.get("metric_schema_version", "")), terminal_reason="setup_failed",
                         setup_seconds=max(0.0, monotonic() - start), ended_at=datetime.now(timezone.utc).isoformat(),
                         launch_id=launch_id, journal_pid=journal_pid, isolation_verified=isolation_verified,
                         denied_write_count=denied_writes, escaped_write_count=escaped_writes,
                         evidence=(reason,))

    @staticmethod
    def add_fault(current: str, next_fault: str) -> str:
        return "; ".join(part for part in (current, next_fault) if part)

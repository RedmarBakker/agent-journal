from datetime import datetime, timezone
import fcntl
import json
import multiprocessing
import os
from pathlib import Path
import pickle
import stat
import sys
import tempfile
import time
from typing import Callable

from tests.lab.batch import Batch
from tests.lab.measurement import Measurement
from tests.lab.network_reading import NETWORK_METRICS, NetworkReading
from tests.lab.run_reading import RUN_METRICS, RunReading
from tests.lab.run_record import RunRecord
from tests.lab.run_request import RunRequest


RunOne = Callable[[RunRequest], RunRecord]


class BatchRunner:
    def __init__(
        self,
        run_one: RunOne,
        lab_home: Path | None = None,
        checkout: Path | None = None,
        workers: int | None = None,
    ) -> None:
        self.run_one = run_one
        self.lab_home = lab_home
        self.checkout = checkout or Path(__file__).resolve().parents[2]
        self.workers = workers

    def run(self, batch: Batch) -> Path:
        pickle.dumps(self.run_one)
        self.worker_count(batch)
        lab_home = self.private_home()
        self.private_directory(lab_home)
        self.private_directory(lab_home / "batches")
        self.private_directory(lab_home / "roots")
        self.private_directory(lab_home / "homes")
        batch_folder = lab_home / "batches" / batch.batch_id
        self.private_directory(batch_folder.parent)
        self.private_directory(batch_folder)
        with self.batch_lock(batch_folder / "batch.lock"):
            manifest = batch.canonical(batch.manifest(lab_home))
            self.immutable_manifest(batch_folder / "manifest.json", manifest)
            requests = batch.requests(lab_home)
            records = self.existing_records(requests)
            pending = tuple(request for request in requests if request.run_id not in records)
            self.prepare_runs(pending)
            self.execute(batch, pending, records)
            lines = tuple(records[request.run_id] for request in requests)
            jsonl = "".join(f"{line}\n" for line in lines)
            summary = self.summary(lines)
            aggregate, summary_path = batch_folder / "runs.jsonl", batch_folder / "summary.json"
            old_aggregate = aggregate.stat().st_size if aggregate.is_file() else 0
            old_summary = summary_path.stat().st_size if summary_path.is_file() else 0
            total = self.storage_used(lab_home, batch.batch_id) - old_aggregate - old_summary
            total += len(jsonl.encode()) + len(summary.encode())
            if total > batch.caps.max_storage_bytes:
                raise ValueError("the batch exceeded its declared storage cap")
            self.atomic_write(aggregate, jsonl)
            self.atomic_write(summary_path, summary)
        return batch_folder / "runs.jsonl"

    def execute(self, batch: Batch, requests: tuple[RunRequest, ...], records: dict[str, str]) -> None:
        context = multiprocessing.get_context("spawn")
        active: dict[multiprocessing.Process, tuple[RunRequest, float, datetime]] = {}
        waiting = iter(requests)
        exhausted = False
        began = time.monotonic()
        while active or not exhausted:
            if time.monotonic() - began >= batch.caps.batch_deadline_seconds:
                self.finish_active(active, records, "capped", "batch deadline reached")
                for request in waiting:
                    self.abort_before_start(request, "batch deadline reached before run start")
                    records[request.run_id] = self.existing_record(request)
                return
            while len(active) < self.worker_count(batch) and not exhausted:
                try:
                    request = next(waiting)
                except StopIteration:
                    exhausted = True
                    break
                process = context.Process(target=self.execute_one, args=(self.run_one, request))
                started_at = datetime.now(timezone.utc)
                self.start_private(process, request)
                active[process] = (request, time.monotonic(), started_at)
            for process, (request, started, started_at) in tuple(active.items()):
                elapsed = time.monotonic() - started
                if process.is_alive() and elapsed >= batch.caps.run_deadline_seconds:
                    process.terminate()
                    process.join()
                    if not request.result.is_file():
                        self.write_terminal(request, "capped", "run deadline reached", started_at)
                    records[request.run_id] = self.existing_record(request)
                    del active[process]
                elif not process.is_alive():
                    process.join()
                    if request.result.is_file():
                        records[request.run_id] = self.existing_record(request)
                    else:
                        failure = request.result.with_name("failure.json")
                        kind = json.loads(failure.read_text()).get("type", "worker exited without a result") if failure.is_file() else "worker exited without a result"
                        self.write_terminal(request, "faulted", str(kind), started_at)
                        records[request.run_id] = self.existing_record(request)
                    del active[process]
            if active:
                time.sleep(0.01)

    def execute_one(self, run_one: RunOne, request: RunRequest) -> None:
        try:
            self.worker_environment(request)
            os.chdir(request.root)
            result = run_one(request)
            self.validate_record(result, request)
            self.atomic_write(request.result, result.json_line() + "\n")
        except BaseException as failure:
            self.atomic_write(request.result.with_name("failure.json"), json.dumps({"type": type(failure).__name__}) + "\n")
            raise

    def validate_record(self, record: RunRecord, request: RunRequest) -> None:
        if not isinstance(record, RunRecord):
            raise TypeError("the run adapter must return a RunRecord")
        actual = (
            record.run_id, record.attempt, record.scenario, record.scenario_version, record.business_type,
            record.design_digest, record.settings_digest, record.seed, record.journal_commit,
            record.organization_commit, record.provider, record.simulated, record.model,
            record.metric_schema_version,
        )
        expected = (
            request.run_id, request.attempt, request.scenario.name, request.scenario.version,
            request.scenario.business_type, request.design.digest, request.design.settings_digest,
            request.seed, request.source_commit, request.organization_commit, request.provider,
            True, request.model, request.metric_schema_version,
        )
        if actual != expected:
            raise ValueError("the run adapter returned a record outside its pinned simulated run")

    def existing_records(self, requests: tuple[RunRequest, ...]) -> dict[str, str]:
        records = {}
        for request in requests:
            if request.result.is_file():
                records[request.run_id] = self.existing_record(request)
            elif request.root.exists() or request.home.exists() or request.result.parent.exists():
                raise ValueError(f"run {request.run_id} has an incomplete attempt; create a new batch attempt")
        return records

    def existing_record(self, request: RunRequest) -> str:
        content = request.result.read_text()
        record = json.loads(content)
        actual = (
            record.get("run_id"), record.get("attempt"), record.get("scenario"),
            record.get("scenario_version"), record.get("business_type"), record.get("design_digest"),
            record.get("settings_digest"), record.get("seed"), record.get("journal_commit"),
            record.get("organization_commit"), record.get("provider"), record.get("simulated"),
            record.get("model"), record.get("metric_schema_version"),
        )
        expected = (
            request.run_id, request.attempt, request.scenario.name, request.scenario.version,
            request.scenario.business_type, request.design.digest, request.design.settings_digest,
            request.seed, request.source_commit, request.organization_commit, request.provider, True,
            request.model, request.metric_schema_version,
        )
        if actual != expected:
            raise ValueError(f"run result for {request.run_id} does not match its manifest")
        self.metric_names(record, "reading", RUN_METRICS)
        self.metric_names(record, "network", NETWORK_METRICS)
        return content.rstrip("\n")

    @staticmethod
    def metric_names(record: dict, section: str, expected: tuple[str, ...]) -> None:
        names = tuple(item["name"] for item in record[section]["measurements"])
        if names != expected:
            raise ValueError(f"run result does not include every {section} metric")

    def prepare_runs(self, requests: tuple[RunRequest, ...]) -> None:
        for request in requests:
            self.private_directory(request.root.parent)
            self.private_directory(request.home.parent)
            self.private_directory(request.result.parent.parent)
            self.private_directory(request.result.parent)
            request.root.mkdir(mode=0o700)
            request.home.mkdir(mode=0o700)
            self.private_directory(request.home / "tmp")

    def terminal(self, request: RunRequest, reason: str, message: str) -> RunRecord:
        now = datetime.now(timezone.utc)
        reading = RunReading.missing(message, request.metric_schema_version)
        network = NetworkReading.missing(message, request.metric_schema_version)
        unknown_setup = Measurement(None, "missing", message, 0, None, (), request.metric_schema_version)
        return RunRecord(
            request.run_id, request.attempt, request.scenario.name, request.scenario.version,
            request.scenario.business_type, request.design.digest, request.design.settings_digest, request.seed,
            request.source_commit, request.organization_commit, request.provider, request.model, True,
            request.metric_schema_version, now, now, reason, unknown_setup, reading, network,
        )

    def abort_before_start(self, request: RunRequest, reason: str) -> None:
        record = self.terminal(request, "aborted", reason)
        measurement = Measurement(None, "not_applicable", reason, 0, None, (), request.metric_schema_version)
        setup = Measurement(None, "not_applicable", reason, 0, None, (), request.metric_schema_version)
        reading = record.reading.with_measurement("minutes_to_done", measurement)
        record = RunRecord(
            record.run_id, record.attempt, record.scenario, record.scenario_version, record.business_type,
            record.design_digest, request.design.settings_digest, record.seed, record.journal_commit,
            record.organization_commit, record.provider, record.model, record.simulated,
            record.metric_schema_version, record.observation_started_at, record.observation_ended_at,
            record.terminal_reason, setup, reading, record.network,
        )
        self.atomic_write(request.result, record.json_line() + "\n")

    def write_terminal(self, request: RunRequest, reason: str, message: str, started_at: datetime) -> None:
        record = self.terminal(request, reason, message)
        record = RunRecord(
            record.run_id, record.attempt, record.scenario, record.scenario_version,
            record.business_type, record.design_digest, record.settings_digest, record.seed,
            record.journal_commit, record.organization_commit, record.provider, record.model,
            record.simulated, record.metric_schema_version, started_at, datetime.now(timezone.utc),
            record.terminal_reason, record.setup_minutes, record.reading, record.network,
        )
        self.atomic_write(request.result, record.json_line() + "\n")

    def finish_active(
        self,
        active: dict[multiprocessing.Process, tuple[RunRequest, float, datetime]],
        records: dict[str, str],
        reason: str,
        message: str,
    ) -> None:
        for process, (request, _, started_at) in tuple(active.items()):
            if process.is_alive():
                process.terminate()
            process.join()
            if not request.result.is_file():
                self.write_terminal(request, reason, message, started_at)
            records[request.run_id] = self.existing_record(request)
            del active[process]

    def worker_count(self, batch: Batch) -> int:
        workers = self.workers if self.workers is not None else min(batch.caps.max_processes, max(1, (os.cpu_count() or 2) - 2))
        if workers < 1 or workers > batch.caps.max_processes:
            raise ValueError("worker count exceeds the manifest's process cap")
        return workers

    def private_home(self) -> Path:
        raw = self.lab_home or Path(os.environ.get("LAB_HOME", Path.home() / "journal-lab"))
        if not raw.expanduser().is_absolute():
            raise ValueError("LAB_HOME must be absolute")
        resolved = raw.expanduser().resolve()
        checkout = self.checkout.resolve()
        if resolved == checkout or resolved in checkout.parents or checkout in resolved.parents or ".journal" in resolved.parts:
            raise ValueError("LAB_HOME must be outside source checkouts and journal homes")
        return resolved

    @staticmethod
    def private_directory(path: Path) -> None:
        if path.is_symlink():
            raise ValueError(f"lab directories cannot be symlinks: {path}")
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        if path.is_symlink():
            raise ValueError(f"lab directories cannot be symlinks: {path}")
        if stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise PermissionError(f"lab path is not private: {path}")

    @staticmethod
    def batch_lock(path: Path):
        if path.is_symlink():
            raise ValueError("batch lock cannot be a symlink")
        path.touch(mode=0o600, exist_ok=True)
        os.chmod(path, 0o600)
        stream = path.open("r+")
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return stream

    def immutable_manifest(self, path: Path, content: str) -> None:
        if path.exists():
            if path.read_text() != content:
                raise ValueError("batch manifest is immutable; changed inputs need a new batch ID")
            return
        self.atomic_write(path, content)

    @staticmethod
    def atomic_write(path: Path, content: str) -> None:
        descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".lab-write-")
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        except BaseException:
            Path(temporary).unlink(missing_ok=True)
            raise

    def summary(self, lines: tuple[str, ...]) -> str:
        records = [json.loads(line) for line in lines]
        metrics = {}
        for section in ("reading", "network"):
            names = RUN_METRICS if section == "reading" else NETWORK_METRICS
            by_name = {name: {status: 0 for status in ("observed", "partial", "missing", "not_applicable", "censored")} for name in names}
            for record in records:
                for item in record[section]["measurements"]:
                    by_name[item["name"]][item["measurement"]["status"]] += 1
            metrics[section] = by_name
        terminal_reasons = {}
        for record in records:
            reason = record["terminal_reason"]
            terminal_reasons[reason] = terminal_reasons.get(reason, 0) + 1
        summary = {"run_count": len(records), "terminal_reasons": terminal_reasons, "metrics": metrics}
        return json.dumps(summary, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"

    @staticmethod
    def storage_used(lab_home: Path, batch_id: str) -> int:
        folders = (lab_home / "batches" / batch_id, lab_home / "roots" / batch_id, lab_home / "homes" / batch_id)
        paths = tuple(path for folder in folders if folder.exists() for path in folder.rglob("*"))
        if any(path.is_symlink() for path in paths):
            raise ValueError("lab artifacts cannot point outside their run roots")
        return sum(path.stat().st_size for path in paths if path.is_file())

    def start_private(self, process: multiprocessing.Process, request: RunRequest) -> None:
        previous = dict(os.environ)
        os.environ.clear()
        os.environ.update({"HOME": str(request.home), "TMPDIR": str(request.home / "tmp"), "PATH": str(Path(sys.executable).parent)})
        try:
            process.start()
        finally:
            os.environ.clear()
            os.environ.update(previous)

    @staticmethod
    def worker_environment(request: RunRequest) -> None:
        os.environ.clear()
        os.environ.update({"HOME": str(request.home), "TMPDIR": str(request.home / "tmp"), "PATH": str(Path(sys.executable).parent)})

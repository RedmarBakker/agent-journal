import copy
import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Callable

from supervisor_bridge.contracts import ContractError, RunReference, bounded_cursor


DEFAULT_STATE_DIR = Path("/var/lib/journal-supervisor/transport")
STATE_FILE = "bridge-state.json"


class StateError(RuntimeError):
    """The transport state cannot be read or safely replaced."""


class StateStore:
    """Transport-only cursor, admitted run, health, retry and receipt state."""

    def __init__(self, directory: Path | str):
        self.directory = Path(directory)
        self.path = self.directory / STATE_FILE
        self.lock_path = self.directory / ".bridge-state.lock"
        self.hook_lock_path = self.directory / ".bridge-hook.lock"

    def snapshot(self) -> dict:
        with self.locked():
            return copy.deepcopy(self.read_locked())

    def active_run(self) -> RunReference | None:
        raw = self.snapshot()["active_run"]
        return RunReference.from_reference(raw) if raw else None

    def observation_cursor(self) -> str | None:
        return bounded_cursor(self.snapshot()["observation_cursor"])

    def record_admitted(self, run: RunReference) -> None:
        def change(state: dict) -> None:
            active = state["active_run"]
            receipt = state["receipt"]
            if active and active != run.to_dict() and not self.receipt_terminal(receipt):
                raise StateError("a different fenced run is still active")
            same_run = active == run.to_dict()
            if not same_run:
                state["receipt"] = None
                if state["blocked_run"] != run.to_dict():
                    state["blocked_run"] = None
            state.update({
                "active_run": run.to_dict(),
                "hook_status": state["hook_status"] if same_run else "pending",
                "hook_attempts": state["hook_attempts"] if same_run else 0,
                "budget_gate": state["budget_gate"] if same_run else "unverified",
                "last_admission": "admitted",
                "last_error": "",
                "health": "up",
                "usage_settlement": "unknown_cost",
            })
        self.update(change)

    def record_skipped(self, reason: str) -> None:
        if reason not in {"empty", "busy", "ineligible", "stale_evidence", "budget_exhausted", "unknown_cost", "revoked", "needs_owner"}:
            raise ContractError("unsupported admission skip reason")
        self.update(lambda state: state.update({"last_admission": reason, "last_error": "", "health": "up"}))

    def record_failure(self, kind: str, retryable: bool) -> None:
        if kind not in {"service_unavailable", "service_unauthorized", "service_rejected", "hook_unavailable", "hook_unauthorized", "state_conflict"}:
            raise ContractError("unsupported bridge failure")
        def change(state: dict) -> None:
            state["health"] = "down"
            state["last_error"] = kind
            if retryable:
                state["retry_count"] += 1
        self.update(change)

    def record_hook_status(self, status: str) -> None:
        if status not in {"pending", "acknowledged", "uncertain", "unauthorized"}:
            raise ContractError("unsupported hook status")
        self.update(lambda state: state.update({"hook_status": status, "health": "up" if status != "unauthorized" else "down"}))

    def claim_hook(self, run: RunReference, maximum_attempts: int) -> bool:
        """Persist a bounded idempotent hook attempt before sending it."""
        claimed = False
        def change(state: dict) -> None:
            nonlocal claimed
            if state["active_run"] != run.to_dict() or state["hook_status"] in {"acknowledged", "unauthorized"}:
                return
            if state["hook_attempts"] >= maximum_attempts:
                return
            state["hook_attempts"] += 1
            state["hook_status"] = "uncertain"
            state["health"] = "up"
            state["last_error"] = ""
            claimed = True
        self.update(change)
        return claimed

    def record_unknown_cost(self) -> None:
        def change(state: dict) -> None:
            if state["active_run"] is not None:
                state["blocked_run"] = state["active_run"]
            state.update({
                "active_run": None,
                "budget_gate": "unknown_cost",
                "last_admission": "unknown_cost",
                "usage_settlement": "unknown_cost",
                "hook_status": "pending",
                "hook_attempts": 0,
                "health": "down",
                "last_error": "aggregate_budget_unproven",
            })
        self.update(change)

    def record_budget_verified(self, run: RunReference) -> None:
        def change(state: dict) -> None:
            if state["active_run"] != run.to_dict():
                raise StateError("budget proof does not match the active fenced run")
            state["budget_gate"] = "verified"
            state["usage_settlement"] = "reserved"
        self.update(change)

    def record_receipt(self, receipt: dict, run: RunReference) -> None:
        if receipt.get("action_id") != run.pending_action_id or receipt.get("run_id") != run.run_id or receipt.get("fence") != run.fence:
            raise ContractError("receipt does not match the active fenced run")
        summary = {
            "action_id": receipt["action_id"],
            "run_id": receipt["run_id"],
            "fence": receipt["fence"],
            "status": receipt["status"],
            "verification": receipt["verification"],
            "outcome": receipt["outcome"],
        }
        self.update(lambda state: state.update({
            "receipt": summary,
            "last_admission": "verified" if receipt["status"] == "applied" and receipt["verification"] == "verified" else state["last_admission"],
            "usage_settlement": "unavailable",
            "health": "up",
            "last_error": "",
        }))

    def record_receipt_pending(self) -> None:
        self.update(lambda state: state.update({"health": "up", "last_error": "receipt_pending"}))

    def record_cursor(self, cursor: object) -> None:
        value = bounded_cursor(cursor)
        self.update(lambda state: state.update({"observation_cursor": value, "health": "up", "last_error": ""}))

    def read_locked(self) -> dict:
        if not self.path.is_file():
            return self.empty_state()
        try:
            state = json.loads(self.path.read_text())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise StateError("transport state is unreadable") from error
        if not isinstance(state, dict) or set(state) != set(self.empty_state()):
            raise StateError("transport state has an unsupported shape")
        if state["observation_cursor"] is not None:
            bounded_cursor(state["observation_cursor"])
        for key in ("active_run", "blocked_run"):
            if state[key] is not None:
                RunReference.from_reference(state[key])
        if state["hook_status"] not in {"pending", "acknowledged", "uncertain", "unauthorized"}:
            raise StateError("transport hook state is unsupported")
        if type(state["hook_attempts"]) is not int or not 0 <= state["hook_attempts"] <= 2:
            raise StateError("transport hook attempts exceed their bound")
        if state["budget_gate"] not in {"unverified", "verified", "unknown_cost"}:
            raise StateError("transport budget state is unsupported")
        if not isinstance(state["last_admission"], str) or not isinstance(state["health"], str) or not isinstance(state["last_error"], str):
            raise StateError("transport status fields are invalid")
        if type(state["retry_count"]) is not int or state["retry_count"] < 0:
            raise StateError("transport retry count is invalid")
        if state["usage_settlement"] not in {"unknown_cost", "reserved", "unavailable"}:
            raise StateError("transport usage settlement is unsupported")
        if state["receipt"] is not None and (
            not isinstance(state["receipt"], dict)
            or set(state["receipt"]) != {"action_id", "run_id", "fence", "status", "verification", "outcome"}
        ):
            raise StateError("transport receipt summary is invalid")
        return state

    def update(self, change: Callable[[dict], object]) -> None:
        with self.locked():
            state = self.read_locked()
            change(state)
            self.write_locked(state)

    def write_locked(self, state: dict) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(prefix=".bridge-state-", dir=self.directory)
        try:
            os.fchmod(handle, 0o660)
            with os.fdopen(handle, "w", encoding="utf-8") as output:
                json.dump(state, output, sort_keys=True, separators=(",", ":"))
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
            directory = os.open(self.directory, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def locked(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o660)
        return StateLock(descriptor)

    def hook_locked(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.hook_lock_path, os.O_CREAT | os.O_RDWR, 0o660)
        return HookLock(descriptor)

    @staticmethod
    def empty_state() -> dict:
        return {
            "observation_cursor": None,
            "active_run": None,
            "blocked_run": None,
            "hook_status": "pending",
            "hook_attempts": 0,
            "budget_gate": "unverified",
            "last_admission": "",
            "health": "unknown",
            "retry_count": 0,
            "last_error": "",
            "usage_settlement": "unknown_cost",
            "receipt": None,
        }

    @staticmethod
    def receipt_terminal(receipt: dict | None) -> bool:
        return bool(receipt and receipt["verification"] in {"verified", "superseded", "not_applied"})


class StateLock:
    """A cross-process exclusive lock for one transport-state update."""

    def __init__(self, descriptor: int):
        self.descriptor = descriptor

    def __enter__(self):
        fcntl.flock(self.descriptor, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, traceback):
        fcntl.flock(self.descriptor, fcntl.LOCK_UN)
        os.close(self.descriptor)


class HookLock:
    """A nonblocking process lock prevents duplicate hook delivery for one run."""

    def __init__(self, descriptor: int):
        self.descriptor = descriptor
        self.acquired = False

    def __enter__(self):
        try:
            fcntl.flock(self.descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.acquired = True
        except BlockingIOError:
            self.acquired = False
        return self.acquired

    def __exit__(self, exc_type, exc, traceback):
        if self.acquired:
            fcntl.flock(self.descriptor, fcntl.LOCK_UN)
        os.close(self.descriptor)

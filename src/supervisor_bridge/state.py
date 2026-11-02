import copy
import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Callable

from supervisor_bridge.contracts import ContractError, RunReference, bounded_cursor, bounded_text


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
        self.provider_lock_path = self.directory / ".bridge-provider.lock"

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
                state["metering"] = self.empty_metering(run)
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
                "usage_settlement": state["usage_settlement"] if same_run else "unknown_cost",
            })
        self.update(change)

    def record_skipped(self, reason: str) -> None:
        if reason not in {"empty", "busy", "ineligible", "stale_evidence", "budget_exhausted", "unknown_cost", "revoked", "needs_owner"}:
            raise ContractError("unsupported admission skip reason")
        self.update(lambda state: state.update({"last_admission": reason, "last_error": "", "health": "up"}))

    def record_failure(self, kind: str, retryable: bool, cause: str = "") -> None:
        if kind not in {"service_unavailable", "service_unauthorized", "service_rejected", "hook_unavailable", "hook_unauthorized", "state_conflict"}:
            raise ContractError("unsupported bridge failure")
        if cause:
            bounded_text(cause, "transport failure cause", 1, 16)
        def change(state: dict) -> None:
            state["health"] = "down"
            state["last_error"] = f"{kind}: {cause}" if cause else kind
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
            state["metering"].update({"status": "unknown_cost", "pending_request": None, "preflight_input_tokens": None})
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
            if state["metering"]["run_ref"] != run.to_dict() or state["metering"]["limits"] is None:
                raise StateError("budget proof has no grant token limits for the active run")
            state["budget_gate"] = "verified"
            receipt = state["receipt"]
            if (
                receipt is None
                or receipt["action_id"] != run.pending_action_id
                or receipt["run_id"] != run.run_id
                or receipt["fence"] != run.fence
            ):
                state["usage_settlement"] = "reserved"
        self.update(change)

    def record_budget_limits(self, run: RunReference, limits: dict) -> None:
        expected = {"max_input_tokens_per_turn", "max_output_tokens_per_turn", "max_provider_requests_per_turn"}
        if not isinstance(limits, dict) or set(limits) != expected:
            raise ContractError("grant token limits have an unsupported shape")
        for key, value in limits.items():
            if type(value) is not int or value < 1:
                raise ContractError(f"{key} must be a positive integer")

        def change(state: dict) -> None:
            if state["active_run"] != run.to_dict():
                raise StateError("grant token limits do not match the active fenced run")
            metering = state["metering"]
            if metering["run_ref"] != run.to_dict():
                raise StateError("grant token limits do not match the metered run")
            if metering["limits"] is not None and metering["limits"] != limits:
                raise StateError("grant token limits changed during the admitted run")
            metering["limits"] = dict(limits)
            if metering["status"] == "awaiting_limits":
                metering["status"] = "ready"
        self.update(change)

    def metering_state(self, run: RunReference) -> dict:
        result = self.snapshot()["metering"]
        if result["run_ref"] != run.to_dict():
            raise StateError("metering state does not match the active fenced run")
        return result

    def can_start_provider_requests(self, run: RunReference, count: int) -> bool:
        if type(count) is not int or count < 1:
            raise ContractError("provider request reservation must be positive")
        state = self.metering_state(run)
        return (
            state["limits"] is not None
            and state["status"] in {"ready", "known"}
            and state["pending_request"] is None
            and state["provider_requests"] + count <= state["limits"]["max_provider_requests_per_turn"]
        )

    def begin_provider_request(self, run: RunReference, kind: str, retry: bool = False) -> bool:
        if kind not in {"input_count", "generation"}:
            raise ContractError("provider request kind is not supported")
        started = False

        def change(state: dict) -> None:
            nonlocal started
            metering = state["metering"]
            if (
                state["active_run"] != run.to_dict()
                or state["budget_gate"] != "verified"
                or metering["run_ref"] != run.to_dict()
                or metering["limits"] is None
                or metering["status"] not in {"ready", "known"}
                or metering["pending_request"] is not None
            ):
                return
            if metering["provider_requests"] >= metering["limits"]["max_provider_requests_per_turn"]:
                metering["status"] = "capped"
                return
            if kind == "generation" and metering["preflight_input_tokens"] is None:
                return
            if kind == "input_count" and metering["preflight_input_tokens"] is not None:
                return
            metering["provider_requests"] += 1
            metering["provider_retries"] += int(retry)
            metering["pending_request"] = kind
            started = True

        self.update(change)
        return started

    def record_input_token_count(self, run: RunReference, count: int) -> bool:
        if type(count) is not int or count < 0:
            raise ContractError("provider input token count is invalid")
        within_cap = False

        def change(state: dict) -> None:
            nonlocal within_cap
            metering = state["metering"]
            if state["active_run"] != run.to_dict() or metering["pending_request"] != "input_count":
                raise StateError("provider input count has no current request reservation")
            metering["pending_request"] = None
            if self.total_input_tokens(metering) + count > metering["limits"]["max_input_tokens_per_turn"]:
                metering["status"] = "capped"
                metering["preflight_input_tokens"] = None
                return
            metering["preflight_input_tokens"] = count
            within_cap = True

        self.update(change)
        return within_cap

    def record_provider_retryable_failure(self, run: RunReference) -> None:
        def change(state: dict) -> None:
            metering = state["metering"]
            if state["active_run"] != run.to_dict() or metering["pending_request"] not in {"input_count", "generation"}:
                raise StateError("provider retry does not match a current request")
            kind = metering["pending_request"]
            metering["pending_request"] = None
            if kind == "input_count":
                metering["preflight_input_tokens"] = None
            state["retry_count"] += 1
            if metering["provider_requests"] >= metering["limits"]["max_provider_requests_per_turn"]:
                metering["status"] = "capped"
        self.update(change)

    def clear_provider_preflight(self, run: RunReference) -> None:
        def change(state: dict) -> None:
            metering = state["metering"]
            if state["active_run"] != run.to_dict() or metering["pending_request"] is not None:
                raise StateError("provider preflight does not match the active run")
            metering["preflight_input_tokens"] = None
        self.update(change)

    def mark_provider_cap(self, run: RunReference) -> None:
        def change(state: dict) -> None:
            metering = state["metering"]
            if state["active_run"] != run.to_dict() or metering["run_ref"] != run.to_dict():
                raise StateError("provider cap does not match the active fenced run")
            if metering["pending_request"] is None:
                metering["status"] = "capped"
        self.update(change)

    def record_provider_usage(
        self,
        run: RunReference,
        input_tokens: int,
        output_tokens: int,
        cache_creation_input_tokens: int,
        cache_read_input_tokens: int,
    ) -> bool:
        usage = (
            (input_tokens, "input_tokens"),
            (output_tokens, "output_tokens"),
            (cache_creation_input_tokens, "cache_creation_input_tokens"),
            (cache_read_input_tokens, "cache_read_input_tokens"),
        )
        for value, name in usage:
            if type(value) is not int or value < 0:
                raise ContractError(f"provider {name} is invalid")
        within_cap = False

        def change(state: dict) -> None:
            nonlocal within_cap
            metering = state["metering"]
            if state["active_run"] != run.to_dict() or metering["pending_request"] != "generation":
                raise StateError("provider usage has no current generation reservation")
            if metering["preflight_input_tokens"] != (
                input_tokens + cache_creation_input_tokens + cache_read_input_tokens
            ):
                self.block_metering_locked(state, run)
                state["health"] = "down"
                state["last_error"] = "provider_usage_mismatch"
                return
            metering["input_tokens"] += input_tokens
            metering["output_tokens"] += output_tokens
            metering["cache_creation_input_tokens"] += cache_creation_input_tokens
            metering["cache_read_input_tokens"] += cache_read_input_tokens
            metering["pending_request"] = None
            metering["preflight_input_tokens"] = None
            if (
                self.total_input_tokens(metering) > metering["limits"]["max_input_tokens_per_turn"]
                or metering["output_tokens"] > metering["limits"]["max_output_tokens_per_turn"]
            ):
                self.block_metering_locked(state, run)
                state["health"] = "down"
                state["last_error"] = "provider_usage_overrun"
                return
            if (
                self.total_input_tokens(metering) == metering["limits"]["max_input_tokens_per_turn"]
                or metering["output_tokens"] == metering["limits"]["max_output_tokens_per_turn"]
                or metering["provider_requests"] == metering["limits"]["max_provider_requests_per_turn"]
            ):
                metering["status"] = "capped"
            else:
                metering["status"] = "known"
            within_cap = True

        self.update(change)
        return within_cap

    def record_provider_unknown_cost(self, run: RunReference, reason: str) -> None:
        if reason not in {"provider_usage_missing", "provider_usage_mismatch", "provider_request_uncertain", "provider_unauthorized"}:
            raise ContractError("provider failure reason is unsupported")

        def change(state: dict) -> None:
            if state["active_run"] != run.to_dict():
                raise StateError("provider failure does not match the active fenced run")
            self.block_metering_locked(state, run)
            state["health"] = "down"
            state["last_error"] = reason
        self.update(change)

    @staticmethod
    def block_metering_locked(state: dict, run: RunReference) -> None:
        state["blocked_run"] = run.to_dict()
        state["active_run"] = None
        state["budget_gate"] = "unknown_cost"
        state["usage_settlement"] = "unknown_cost"
        state["metering"].update({"status": "unknown_cost", "pending_request": None, "preflight_input_tokens": None})

    def record_receipt(self, receipt: dict, run: RunReference) -> None:
        if receipt.get("action_id") != run.pending_action_id or receipt.get("run_id") != run.run_id or receipt.get("fence") != run.fence:
            raise ContractError("receipt does not match the active fenced run")

        def change(state: dict) -> None:
            metering = state["metering"]
            uncertain = metering["pending_request"] is not None
            previous = state["receipt"]
            same_receipt = previous is not None and (
                previous["action_id"] == run.pending_action_id
                and previous["run_id"] == run.run_id
                and previous["fence"] == run.fence
            )
            already_settled = same_receipt and state["usage_settlement"] == "settled"
            settled = (
                metering["run_ref"] == run.to_dict()
                and (metering["status"] in {"known", "capped"} or already_settled)
                and metering["provider_requests"] > 0
                and not uncertain
            )
            summary = {
                "action_id": receipt["action_id"],
                "run_id": receipt["run_id"],
                "fence": receipt["fence"],
                "status": receipt["status"],
                "verification": receipt["verification"],
                "outcome": receipt["outcome"],
                "usage": self.usage_summary(metering) if settled and not already_settled else previous["usage"] if already_settled else None,
            }
            if uncertain:
                self.block_metering_locked(state, run)
                state["last_error"] = "provider_request_uncertain"
            else:
                metering["status"] = "settled"
                metering["preflight_input_tokens"] = None
            state.update({
                "receipt": summary,
                "last_admission": "verified" if receipt["status"] == "applied" and receipt["verification"] == "verified" else state["last_admission"],
                "usage_settlement": "unknown_cost" if uncertain else "settled" if settled else "unavailable",
                "health": "down" if uncertain else "up",
                "last_error": "provider_request_uncertain" if uncertain else "",
            })

        self.update(change)

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
        if not isinstance(state, dict):
            raise StateError("transport state has an unsupported shape")
        previous_fields = set(self.empty_state()) - {"metering"}
        if set(state) == previous_fields:
            old_run = state["active_run"]
            state["metering"] = self.empty_metering(RunReference.from_reference(old_run) if old_run else None)
            if old_run:
                state.update({
                    "active_run": None,
                    "blocked_run": old_run,
                    "budget_gate": "unknown_cost",
                    "last_admission": "unknown_cost",
                    "usage_settlement": "unknown_cost",
                    "health": "down",
                    "last_error": "usage_before_proxy_unknown",
                })
            if state["receipt"] is not None:
                state["receipt"]["usage"] = None
            self.write_locked(state)
        old_metering_fields = {
            "run_ref", "limits", "input_tokens", "output_tokens", "cached_tokens", "provider_requests",
            "provider_retries", "status", "pending_request", "preflight_input_tokens",
        }
        if (
            set(state) == set(self.empty_state())
            and isinstance(state.get("metering"), dict)
            and set(state["metering"]) == old_metering_fields
        ):
            old_run = state["active_run"]
            state["metering"] = self.empty_metering(RunReference.from_reference(old_run) if old_run else None)
            if old_run:
                state.update({
                    "active_run": None,
                    "blocked_run": old_run,
                    "budget_gate": "unknown_cost",
                    "last_admission": "unknown_cost",
                    "usage_settlement": "unknown_cost",
                    "health": "down",
                    "last_error": "usage_before_anthropic_route_unknown",
                })
                state["metering"]["status"] = "unknown_cost"
            self.write_locked(state)
        if set(state) != set(self.empty_state()):
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
        if state["usage_settlement"] not in {"unknown_cost", "reserved", "unavailable", "settled"}:
            raise StateError("transport usage settlement is unsupported")
        if state["receipt"] is not None and (
            not isinstance(state["receipt"], dict)
            or set(state["receipt"]) != {"action_id", "run_id", "fence", "status", "verification", "outcome", "usage"}
        ):
            raise StateError("transport receipt summary is invalid")
        metering = state["metering"]
        if not isinstance(metering, dict) or set(metering) != {
            "run_ref", "limits", "input_tokens", "output_tokens", "cache_creation_input_tokens",
            "cache_read_input_tokens", "provider_requests",
            "provider_retries", "status", "pending_request", "preflight_input_tokens",
        }:
            raise StateError("provider metering state has an unsupported shape")
        if metering["run_ref"] is not None:
            RunReference.from_reference(metering["run_ref"])
        limits = metering["limits"]
        if limits is not None and (
            not isinstance(limits, dict)
            or set(limits) != {"max_input_tokens_per_turn", "max_output_tokens_per_turn", "max_provider_requests_per_turn"}
            or any(type(value) is not int or value < 1 for value in limits.values())
        ):
            raise StateError("provider metering grant limits are invalid")
        for key in (
            "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
            "provider_requests", "provider_retries",
        ):
            if type(metering[key]) is not int or metering[key] < 0:
                raise StateError("provider metering totals are invalid")
        if metering["status"] not in {"awaiting_limits", "ready", "known", "capped", "settled", "unknown_cost"}:
            raise StateError("provider metering status is unsupported")
        if metering["pending_request"] not in {None, "input_count", "generation"}:
            raise StateError("provider metering request state is unsupported")
        if metering["preflight_input_tokens"] is not None and (
            type(metering["preflight_input_tokens"]) is not int or metering["preflight_input_tokens"] < 0
        ):
            raise StateError("provider input token preflight is invalid")
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

    def provider_locked(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.provider_lock_path, os.O_CREAT | os.O_RDWR, 0o660)
        return ProviderLock(descriptor)

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
            "metering": StateStore.empty_metering(),
        }

    @staticmethod
    def empty_metering(run: RunReference | None = None) -> dict:
        return {
            "run_ref": run.to_dict() if run else None,
            "limits": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
            "provider_requests": 0,
            "provider_retries": 0,
            "status": "awaiting_limits" if run else "unknown_cost",
            "pending_request": None,
            "preflight_input_tokens": None,
        }

    @staticmethod
    def usage_summary(metering: dict) -> dict:
        return {
            "input_tokens": metering["input_tokens"],
            "output_tokens": metering["output_tokens"],
            "cache_creation_input_tokens": metering["cache_creation_input_tokens"],
            "cache_read_input_tokens": metering["cache_read_input_tokens"],
            "total_input_tokens": StateStore.total_input_tokens(metering),
            "provider_requests": metering["provider_requests"],
            "provider_retries": metering["provider_retries"],
        }

    def settlement_usage(self, run: RunReference) -> dict:
        state = self.snapshot()
        metering = state["metering"]
        if (state["active_run"] != run.to_dict() or state["budget_gate"] != "verified"
                or metering["run_ref"] != run.to_dict() or metering["limits"] is None
                or metering["status"] not in {"known", "capped"}
                or metering["pending_request"] is not None or metering["provider_requests"] < 1):
            raise StateError("the admitted run has no complete provider usage to settle")
        if (self.total_input_tokens(metering) > metering["limits"]["max_input_tokens_per_turn"]
                or metering["output_tokens"] > metering["limits"]["max_output_tokens_per_turn"]
                or metering["provider_requests"] > metering["limits"]["max_provider_requests_per_turn"]):
            raise StateError("the provider usage exceeds the admitted run limits")
        return self.usage_summary(metering)

    def record_usage_settlement(self, run: RunReference, settlement: dict) -> None:
        if (not isinstance(settlement, dict)
                or set(settlement) != {"status", "usage_id", "run_id", "fence", "usage_status", "duplicate"}
                or settlement["status"] != "settled" or type(settlement["usage_id"]) is not int
                or settlement["usage_id"] < 1 or settlement["run_id"] != run.run_id
                or type(settlement["fence"]) is not int or settlement["fence"] != run.fence
                or settlement["usage_status"] != "known" or type(settlement["duplicate"]) is not bool):
            raise ContractError("journal usage settlement does not match the admitted run")

        def change(state: dict) -> None:
            metering = state["metering"]
            if (state["active_run"] != run.to_dict() or metering["run_ref"] != run.to_dict()
                    or metering["status"] not in {"known", "capped"}
                    or metering["pending_request"] is not None):
                raise StateError("journal usage settlement has no complete active provider meter")
            state["usage_settlement"] = "settled"
            state["health"] = "up"
            state["last_error"] = ""

        self.update(change)

    @staticmethod
    def total_input_tokens(metering: dict) -> int:
        return (
            metering["input_tokens"]
            + metering["cache_creation_input_tokens"]
            + metering["cache_read_input_tokens"]
        )

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


class ProviderLock(HookLock):
    """A nonblocking process lock keeps a provider run's meter serial."""

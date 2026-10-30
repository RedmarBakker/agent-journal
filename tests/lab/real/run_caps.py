import fcntl
import json
import math
import os
import stat
import tempfile
import time
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable, Mapping


RUN_LIMITS = ("run_wall_minutes", "run_sessions", "run_concurrent_sessions", "turns_per_session", "run_turns")
BATCH_LIMITS = ("batch_run_count", "batch_session_count", "batch_turns", "batch_run_minutes", "batch_elapsed_minutes")
BATCH_CAPS = frozenset((*BATCH_LIMITS, "batch_max_usd"))
INTEGER_LIMITS = frozenset({"run_sessions", "run_concurrent_sessions", "turns_per_session", "run_turns",
                            "batch_run_count", "batch_session_count", "batch_turns"})


class RunCaps:
    """Validate owner-selected caps and persist each run, session and request reservation before launch."""

    def __init__(self, run_id: str, run_caps: Mapping[str, object], batch_caps: Mapping[str, object], ledger: Path,
                 watchdog: object | None = None, clock: Callable[[], float] = time.monotonic) -> None:
        self.run_id, self.run_caps, self.batch_caps = run_id, dict(run_caps), dict(batch_caps)
        self.ledger, self.watchdog, self.clock = ledger, watchdog, clock
        self.validate(self.run_caps, RUN_LIMITS)
        self.validate(self.batch_caps, BATCH_LIMITS)
        self.validate_cost_cap(self.run_caps)
        self.validate_cost_cap(self.batch_caps, "batch_max_usd")
        token_limits = self.run_caps.get("request_token_limits", {})
        if not isinstance(token_limits, Mapping):
            raise ValueError("request token limits must be a table")
        for key, value in token_limits.items():
            if key not in {"input_tokens", "output_tokens"} or type(value) is not int or value <= 0:
                raise ValueError("request token limits need positive input_tokens or output_tokens")

    @classmethod
    def validate(cls, caps: Mapping[str, object], required: tuple[str, ...]) -> None:
        if caps.get("state") != "selected":
            raise ValueError("real run caps are owner_pending until every required value is selected")
        for key in required:
            value = cls.positive(caps.get(key), key)
            if key in INTEGER_LIMITS and not value.is_integer():
                raise ValueError(f"{key} must be a whole number")

    @staticmethod
    def positive(value: object, field: str) -> float:
        if type(value) not in (int, float) or not math.isfinite(float(value)) or value <= 0:
            raise ValueError(f"{field} must be an explicit positive finite number")
        return float(value)

    @classmethod
    def validate_cost_cap(cls, caps: Mapping[str, object], field: str = "max_usd") -> None:
        value = caps.get(field, "unknown")
        if value == "not_applicable":
            reason = caps.get("not_applicable_reason")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(f"{field} may be not_applicable only with an owner-approved reason")
            return
        if value == "unknown":
            if caps.get("unknown_cost_accepted") is not True:
                raise ValueError("unknown billable cost must be explicitly accepted in the manifest")
            return
        cls.money(value, field)

    @staticmethod
    def money(value: object, field: str) -> Decimal:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError(f"{field} must be a positive finite USD amount") from None
        if not amount.is_finite() or amount <= 0:
            raise ValueError(f"{field} must be a positive finite USD amount")
        return amount

    def reserve_run(self) -> dict[str, object]:
        with self.locked():
            data = self.read()
            if data.get("quarantined"):
                raise ValueError("batch is quarantined after an unconfirmed stop or cap breach")
            cap = data.get("cap_reached")
            if cap and cap.get("cap") in BATCH_CAPS:
                raise ValueError("a batch cap has already stopped this batch")
            if "batch_deadline" not in data:
                data["batch_deadline"] = self.clock() + self.batch_caps["batch_elapsed_minutes"] * 60
            if self.clock() >= data["batch_deadline"]:
                raise ValueError("batch elapsed-time cap was reached before run admission")
            runs = data.setdefault("runs", {})
            current = runs.get(self.run_id)
            if current:
                if current["run_cap"] != self.run_caps:
                    raise ValueError("a replayed run id cannot change its reserved caps")
                if current.get("finished") or current.get("cap_reached"):
                    raise ValueError("a finished or capped run id cannot be admitted again")
                return current
            reserved = list(runs.values())
            if len(reserved) >= self.batch_caps["batch_run_count"]:
                raise ValueError("batch run count cap would be exceeded")
            total_sessions = sum(run["run_cap"]["run_sessions"] for run in reserved) + self.run_caps["run_sessions"]
            total_turns = sum(run["run_cap"]["run_turns"] for run in reserved) + self.run_caps["run_turns"]
            total_minutes = sum(run["run_cap"]["run_wall_minutes"] for run in reserved) + self.run_caps["run_wall_minutes"]
            if total_sessions > self.batch_caps["batch_session_count"]:
                raise ValueError("batch session reservation exceeds its cap")
            if total_turns > self.batch_caps["batch_turns"]:
                raise ValueError("batch turn reservation exceeds its cap")
            if total_minutes > self.batch_caps["batch_run_minutes"]:
                raise ValueError("batch run-minute reservation exceeds its cap")
            if total_minutes > self.batch_caps["batch_elapsed_minutes"]:
                raise ValueError("batch elapsed deadline is shorter than the run reservations")
            current = {"run_cap": self.run_caps, "sessions": {}, "requests": {}, "watchdog_armed": False,
                       "deadline": self.clock() + self.run_caps["run_wall_minutes"] * 60}
            runs[self.run_id] = current
            self.write(data)
            return current

    def arm_watchdog(self) -> None:
        current = self.reserve_run()
        if self.watchdog is None or not hasattr(self.watchdog, "arm") or not hasattr(self.watchdog, "stop"):
            raise ValueError("runner-owned watchdog is unavailable; real run admission is refused")
        with self.locked():
            data = self.read()
            active = data.get("active_run")
            if active and active != self.run_id:
                raise ValueError("real batches admit only one active run at a time")
            current = self.run(data)
            if current["watchdog_armed"]:
                return
            data["active_run"] = self.run_id
            current["watchdog_arming"] = True
            self.write(data)
        armed = []
        try:
            data = self.read()
            self.arm_deadline(f"batch:{self.ledger.parent.name}", data["batch_deadline"], armed)
            self.arm_deadline(self.run_id, current["deadline"], armed)
        except Exception:
            confirmed = True
            for owner in reversed(armed):
                try:
                    confirmed = self.watchdog.stop(owner, "watchdog admission failed") is True and confirmed
                except Exception:
                    confirmed = False
            with self.locked():
                data = self.read()
                data["runs"][self.run_id].pop("watchdog_arming", None)
                if data.get("active_run") == self.run_id:
                    data.pop("active_run")
                if not confirmed:
                    data["quarantined"] = "watchdog admission rollback was not confirmed"
                self.write(data)
            raise
        with self.locked():
            data = self.read()
            current = self.run(data)
            current.pop("watchdog_arming", None)
            current["watchdog_armed"] = True
            self.write(data)

    def arm_deadline(self, owner: str, deadline: float, armed: list[str]) -> None:
        armed.append(owner)
        if self.watchdog.arm(owner, deadline) is not True:
            raise ValueError("external watchdog did not confirm its deadline")

    def finish_run(self, stop_confirmed: bool) -> None:
        with self.locked():
            data = self.read()
            current = data.get("runs", {}).get(self.run_id)
            if current is None:
                return
            watchdog_stopped = True
            if current.get("watchdog_armed"):
                try:
                    watchdog_stopped = self.watchdog.stop(self.run_id, "run finished") is True
                except Exception:
                    watchdog_stopped = False
                current["watchdog_armed"] = False
            if data.get("active_run") == self.run_id:
                data.pop("active_run")
            current["finished"] = stop_confirmed is True and watchdog_stopped
            if not current["finished"]:
                data["quarantined"] = f"owned process stop unconfirmed for run {self.run_id}"
            self.write(data)

    def cancel_before_launch(self) -> None:
        with self.locked():
            data = self.read()
            current = data.get("runs", {}).get(self.run_id)
            if current is None:
                return
            confirmed = True
            if current.get("watchdog_armed"):
                try:
                    confirmed = self.watchdog.stop(self.run_id, "setup failed before plan launch") is True
                except Exception:
                    confirmed = False
                current["watchdog_armed"] = False
            if data.get("active_run") == self.run_id:
                data.pop("active_run")
            current["finished"] = confirmed
            if not confirmed:
                data["quarantined"] = f"watchdog stop unconfirmed before plan launch for run {self.run_id}"
            self.write(data)

    def quarantine(self, reason: str) -> None:
        with self.locked():
            data = self.read()
            current = data.get("runs", {}).get(self.run_id)
            data["quarantined"] = reason
            data["cap_reached"] = {"run_id": self.run_id, "cap": "isolation", "reason": reason, "at": self.clock()}
            confirmed = False
            if current is not None and current.get("watchdog_armed"):
                try:
                    confirmed = self.watchdog.stop(self.run_id, reason) is True
                except Exception:
                    confirmed = False
                if confirmed:
                    current["watchdog_armed"] = False
                    if data.get("active_run") == self.run_id:
                        data.pop("active_run")
            self.write(data)

    def start_session(self, session_id: str) -> dict[str, object]:
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("a provider session needs an identity before it can be admitted")
        with self.locked():
            data = self.read()
            current = self.run(data)
            self.reject_closed(data)
            if not current["watchdog_armed"]:
                raise ValueError("the run watchdog must be armed before a provider session starts")
            sessions = current["sessions"]
            if session_id in sessions:
                active = sum(1 for session in sessions.values() if session["active"])
                if not sessions[session_id]["active"] and active >= self.run_caps["run_concurrent_sessions"]:
                    self.refuse_at_cap(data, "run_concurrent_sessions", "run concurrent-session cap reached")
                sessions[session_id]["active"] = True
                self.write(data)
                return sessions[session_id]
            active = sum(1 for session in sessions.values() if session["active"])
            if len(sessions) >= self.run_caps["run_sessions"]:
                self.refuse_at_cap(data, "run_sessions", "run session cap reached")
            if active >= self.run_caps["run_concurrent_sessions"]:
                self.refuse_at_cap(data, "run_concurrent_sessions", "run concurrent-session cap reached")
            item = {"active": True, "turns": 0}
            sessions[session_id] = item
            self.write(data)
            return item

    def finish_session(self, session_id: str) -> None:
        with self.locked():
            data = self.read()
            session = self.run(data)["sessions"].get(session_id)
            if session:
                session["active"] = False
                self.write(data)

    def reserve_request(self, request_id: str, session_id: str, input_tokens: int = 0, output_tokens: int = 0,
                        maximum_usd: object | None = None) -> dict[str, object]:
        if not isinstance(request_id, str) or not request_id or not isinstance(session_id, str) or not session_id or type(input_tokens) is not int or type(output_tokens) is not int or input_tokens < 0 or output_tokens < 0:
            raise ValueError("a request needs an identity and non-negative token counts")
        with self.locked():
            data = self.read()
            current = self.run(data)
            self.reject_closed(data)
            existing = current["requests"].get(request_id)
            if existing:
                requested_maximum = self.money(maximum_usd, "maximum_usd") if maximum_usd is not None else None
                reserved_maximum = Decimal(existing["reserved_usd"]) if existing["reserved_usd"] is not None else None
                if existing["session_id"] != session_id or existing["input_tokens"] != input_tokens or existing["output_tokens"] != output_tokens:
                    raise ValueError("a replayed request id cannot change its reservation")
                if requested_maximum != reserved_maximum:
                    raise ValueError("a replayed request id cannot change its reserved maximum charge")
                return existing
            session = current["sessions"].get(session_id)
            if not session or not session["active"]:
                raise ValueError("provider requests require an admitted live session")
            if self.clock() >= current["deadline"]:
                self.refuse_at_cap(data, "run_wall_minutes", "run wall-time cap reached")
            if self.clock() >= data["batch_deadline"]:
                self.refuse_at_cap(data, "batch_elapsed_minutes", "batch elapsed-time cap reached")
            run_requests = current["requests"]
            batch_requests = sum(len(run["requests"]) for run in data["runs"].values())
            if len(run_requests) >= self.run_caps["run_turns"]:
                self.refuse_at_cap(data, "run_turns", "provider turn cap reached")
            if batch_requests >= self.batch_caps["batch_turns"]:
                self.refuse_at_cap(data, "batch_turns", "batch provider turn cap reached")
            if session["turns"] >= self.run_caps["turns_per_session"]:
                self.refuse_at_cap(data, "turns_per_session", "provider session turn cap reached")
            token_limits = self.run_caps.get("request_token_limits", {})
            for key, count in (("input_tokens", input_tokens), ("output_tokens", output_tokens)):
                if key in token_limits and count > token_limits[key]:
                    self.refuse_at_cap(data, key, f"provider request {key} cap reached")
            max_usd = self.request_cost(maximum_usd)
            request = {"session_id": session_id, "input_tokens": input_tokens, "output_tokens": output_tokens,
                       "reserved_usd": str(max_usd) if max_usd is not None else None, "status": "reserved"}
            current["requests"][request_id] = request
            session["turns"] += 1
            self.write(data)
            return request

    def settle_request(self, request_id: str, actual_usd: object | None, status: str) -> None:
        if status not in {"completed", "failed", "unknown"}:
            raise ValueError("request settlement must be completed, failed or unknown")
        with self.locked():
            data = self.read()
            request = self.run(data)["requests"].get(request_id)
            if not request:
                raise ValueError("request must be reserved before it is settled")
            actual = self.money(actual_usd, "actual_usd") if actual_usd is not None else None
            reserved = Decimal(request["reserved_usd"]) if request["reserved_usd"] is not None else None
            if request["status"] != "reserved":
                saved_actual = Decimal(request["actual_usd"]) if request.get("actual_usd") is not None else None
                if request["status"] == status and saved_actual == actual:
                    return
                raise ValueError("a settled provider request cannot change its receipt")
            if reserved is not None and actual is not None and actual > reserved:
                data["quarantined"] = f"request {request_id} exceeded its reserved charge"
                data["cap_reached"] = {"run_id": self.run_id, "cap": "charge_reservation",
                                        "reason": "observed request charge exceeded its reserved maximum", "at": self.clock()}
                request["actual_usd"] = str(actual)
                request["status"] = "unknown"
                try:
                    confirmed = self.watchdog.stop(self.run_id, "observed request charge exceeded its reservation") is True if self.watchdog and hasattr(self.watchdog, "stop") else False
                except Exception:
                    confirmed = False
                if confirmed is True:
                    self.run(data)["watchdog_armed"] = False
                    if data.get("active_run") == self.run_id:
                        data.pop("active_run")
                self.write(data)
                raise ValueError("observed request charge exceeded its reserved maximum; quarantine the batch")
            request["actual_usd"] = str(actual) if actual is not None else None
            request["status"] = status
            self.write(data)

    def request_cost(self, value: object | None) -> Decimal | None:
        run_cap = self.run_caps.get("max_usd", "unknown")
        batch_cap = self.batch_caps.get("batch_max_usd", "unknown")
        hard_caps = tuple(cap for cap in (run_cap, batch_cap) if cap not in ("unknown", "not_applicable"))
        if not hard_caps:
            return self.money(value, "maximum_usd") if value is not None else None
        if value is None:
            self.refuse_unbounded_request(self.read())
        maximum = self.money(value, "maximum_usd")
        data = self.read()
        run_reserved = sum((Decimal(item["reserved_usd"]) for item in self.run(data)["requests"].values() if item["reserved_usd"]), Decimal(0))
        if run_cap not in ("unknown", "not_applicable") and run_reserved + maximum > self.money(run_cap, "max_usd"):
            self.refuse_at_cap(data, "max_usd", "request charge reservation reaches the run USD cap")
        if batch_cap not in ("unknown", "not_applicable"):
            batch_reserved = sum((Decimal(item["reserved_usd"]) for run in data.get("runs", {}).values()
                                  for item in run["requests"].values() if item["reserved_usd"]), Decimal(0))
            if batch_reserved + maximum > self.money(batch_cap, "batch_max_usd"):
                self.refuse_at_cap(data, "batch_max_usd", "request charge reservation reaches the batch USD cap")
        return maximum

    def refuse_at_cap(self, data: dict[str, object], cap: str, reason: str) -> None:
        data["cap_reached"] = {"run_id": self.run_id, "cap": cap, "reason": reason, "at": self.clock()}
        try:
            confirmed = self.watchdog.stop(self.run_id, reason) is True if self.watchdog and hasattr(self.watchdog, "stop") else False
        except Exception:
            confirmed = False
        current = self.run(data)
        current["watchdog_armed"] = False
        current["finished"] = confirmed is True
        if confirmed is True and data.get("active_run") == self.run_id:
            data.pop("active_run")
        if confirmed is not True:
            data["quarantined"] = f"stop unconfirmed after {cap} cap"
        self.write(data)
        raise ValueError(reason)

    def refuse_unbounded_request(self, data: dict[str, object]) -> None:
        data["cap_reached"] = {"run_id": self.run_id, "cap": "charge_reservation",
                               "reason": "provider cannot enforce the request maximum required by the selected USD cap",
                               "at": self.clock()}
        try:
            confirmed = self.watchdog.stop(self.run_id, "provider request has no enforceable maximum charge") is True if self.watchdog and hasattr(self.watchdog, "stop") else False
        except Exception:
            confirmed = False
        data["quarantined"] = "selected USD cap cannot be enforced for the provider request"
        if confirmed:
            self.run(data)["watchdog_armed"] = False
            if data.get("active_run") == self.run_id:
                data.pop("active_run")
        self.write(data)
        raise ValueError("a hard USD cap requires a provider-enforced maximum charge for each request")

    def reject_closed(self, data: dict[str, object]) -> None:
        if data.get("quarantined"):
            raise ValueError("batch is quarantined after an unconfirmed stop or cap breach")
        cap = data.get("cap_reached")
        if cap and (cap.get("cap") in BATCH_CAPS or cap.get("run_id") == self.run_id):
            raise ValueError("a reached run or batch cap has stopped this admission")

    def run(self, data: dict[str, object]) -> dict[str, object]:
        try:
            return data["runs"][self.run_id]
        except KeyError:
            raise ValueError("run must reserve its caps before session or request admission") from None

    @contextmanager
    def locked(self):
        self.validate_ledger_path()
        lock_path = self.ledger.with_suffix(".lock")
        if lock_path.is_symlink():
            raise ValueError("reservation lock cannot be a symlink")
        descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077:
                raise ValueError("reservation lock must be a private regular file")
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def read(self) -> dict[str, object]:
        self.validate_ledger_path()
        return json.loads(self.ledger.read_text(encoding="utf-8")) if self.ledger.is_file() else {"runs": {}}

    def write(self, data: dict[str, object]) -> None:
        self.validate_ledger_path()
        descriptor, name = tempfile.mkstemp(prefix=".reservation-", dir=self.ledger.parent)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as target:
                json.dump(data, target, sort_keys=True, separators=(",", ":"), allow_nan=False)
                target.flush()
                os.fsync(target.fileno())
            os.replace(name, self.ledger)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def validate_ledger_path(self) -> None:
        if not self.ledger.is_absolute() or any(part.is_symlink() for part in (self.ledger, *self.ledger.parents)):
            raise ValueError("reservation ledger must use an absolute path without symlinks")
        if not self.ledger.parent.is_dir() or self.ledger.parent.stat().st_mode & 0o077:
            raise ValueError("reservation ledger directory must be private to its owner")
        if self.ledger.exists() and (not self.ledger.is_file() or self.ledger.stat().st_mode & 0o077):
            raise ValueError("reservation ledger must be a private regular file")

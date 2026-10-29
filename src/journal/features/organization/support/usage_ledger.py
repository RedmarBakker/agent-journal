"""Reset-aware, explicitly estimated OpenRig usage for organization plans.

OpenRig reports cumulative cost for a native session.  The ledger turns each
observation into a delta, including a reset when the cumulative value goes
backwards, and keeps account subscription limits in a separate record.
"""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
import threading

from journal.config import Config

ESTIMATE_SOURCE = "OpenRig native-session estimate"


@dataclass(frozen=True)
class UsageEstimate:
    plan_id: int
    amount_usd: float | None
    source: str
    window_start: float | None
    window_end: float | None
    coverage: str
    freshness: str
    status: str
    observed_seats: int = 0
    expected_seats: int | None = None


@dataclass(frozen=True)
class SubscriptionLimits:
    limits: dict[str, dict[str, float]] | None
    source: str
    window: str
    coverage: str
    observed_at: float | None
    freshness: str
    status: str


class UsageLedger:
    """Persist OpenRig cost estimates without treating them as invoices."""

    def __init__(self, config: Config, stale_after_seconds: float = 900.0) -> None:
        self.path = config.home / "runtime" / "organization" / "usage-ledger.json"
        self.stale_after_seconds = stale_after_seconds
        self._lock = threading.RLock()

    def observe(self, plan_id: int, seat: str, native_session: str, cumulative_usd: float, observed_at: float, expected_seats: int | None = None) -> UsageEstimate:
        with self._lock:
            data = self._read()
            key = f"{plan_id}:{seat}"
            previous = data["seats"].get(key, {})
            same_session = previous.get("native_session") == native_session
            previous_total = float(previous.get("native_total_usd", 0.0)) if same_session else 0.0
            current_total = max(0.0, float(cumulative_usd))
            reset = same_session and current_total < previous_total
            delta = current_total if not same_session or reset else current_total - previous_total
            previous["estimated_usd"] = float(previous.get("estimated_usd", 0.0)) + delta
            previous.update({
                "plan_id": plan_id,
                "seat": seat,
                "native_session": native_session,
                "native_total_usd": current_total,
                "first_seen": previous.get("first_seen", observed_at),
                "last_seen": observed_at,
                "source": ESTIMATE_SOURCE,
            })
            data["seats"][key] = previous
            self._write(data)
            return self.estimate_data(data, plan_id, observed_at, expected_seats)

    def estimate(self, plan_id: int, now: float, expected_seats: int | None = None) -> UsageEstimate:
        with self._lock:
            return self.estimate_data(self._read(), plan_id, now, expected_seats)

    def estimate_data(self, data: dict, plan_id: int, now: float, expected_seats: int | None) -> UsageEstimate:
        records = [row for row in data["seats"].values() if int(row["plan_id"]) == plan_id]
        if not records:
            coverage = f"0 of {expected_seats} seats observed" if expected_seats is not None else "0 of unknown seats observed"
            return UsageEstimate(plan_id, None, ESTIMATE_SOURCE, None, None, coverage, "missing", "missing", 0, expected_seats)
        newest = max(float(row["last_seen"]) for row in records)
        stale = any(now - float(row["last_seen"]) > self.stale_after_seconds for row in records)
        partial = expected_seats is not None and len(records) < expected_seats
        coverage = f"{len(records)} of {expected_seats} seats observed" if expected_seats is not None else f"{len(records)} seats observed; expected count unknown"
        return UsageEstimate(
            plan_id,
            sum(float(row["estimated_usd"]) for row in records),
            ESTIMATE_SOURCE,
            min(float(row["first_seen"]) for row in records),
            newest,
            coverage,
            "stale" if stale else "fresh",
            "stale" if stale else "partial" if partial else "estimated",
            len(records),
            expected_seats,
        )

    def record_subscription_limits(self, limits: dict[str, dict[str, float]] | None, source: str, window: str, observed_at: float, coverage: str = "account-wide subscription windows") -> None:
        with self._lock:
            data = self._read()
            data["subscription_limits"] = {
                "limits": None if limits is None else {str(key): {str(name): float(value) for name, value in row.items()} for key, row in limits.items()},
                "source": source,
                "window": window,
                "coverage": coverage,
                "observed_at": observed_at,
            }
            self._write(data)

    def subscription_limits(self, now: float) -> SubscriptionLimits:
        with self._lock:
            value = self._read().get("subscription_limits")
            if not value:
                return SubscriptionLimits(None, "", "", "", None, "missing", "missing")
            observed_at = float(value["observed_at"])
            stale = now - observed_at > self.stale_after_seconds
            limits = value.get("limits")
            return SubscriptionLimits(
                limits,
                str(value["source"]),
                str(value["window"]),
                str(value.get("coverage", "unknown")),
                observed_at,
                "stale" if stale else "fresh",
                "stale" if stale else "available" if limits is not None else "missing",
            )

    def _read(self) -> dict:
        if not self.path.is_file():
            return {"seats": {}, "subscription_limits": None}
        return json.loads(self.path.read_text())

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor, temporary = tempfile.mkstemp(dir=self.path.parent, prefix="usage-")
        try:
            with os.fdopen(descriptor, "w") as stream:
                json.dump(data, stream, sort_keys=True)
                stream.write("\n")
            os.chmod(temporary, 0o600)
            os.replace(temporary, self.path)
            os.chmod(self.path.parent, 0o700)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

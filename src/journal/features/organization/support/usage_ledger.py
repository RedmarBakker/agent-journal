"""Reset-aware, explicitly estimated OpenRig usage for organization plans.

OpenRig reports cumulative cost for a native session.  The ledger turns each
observation into a delta, including a reset when the cumulative value goes
backwards, and keeps account subscription limits in a separate record.
"""

from collections.abc import Iterable
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import tempfile
import threading

from journal.config import Config

ESTIMATE_SOURCE = "OpenRig native-session estimate"
ESTIMATE_LABEL = "Estimated API cost"


@dataclass(frozen=True)
class UsageReading:
    amount_usd: float | None
    source: str
    estimate_kind: str
    native_session_id: str
    window: dict[str, object]
    coverage: str
    freshness: str
    status: str
    source_status: str = ""
    reason: str = ""
    sampled_at: float | None = None


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
    estimate_kind: str = ""
    label: str = ESTIMATE_LABEL


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
        reading = UsageReading(
            cumulative_usd,
            ESTIMATE_SOURCE,
            "OpenRig native-session estimate",
            native_session,
            {},
            "one native session",
            "fresh",
            "estimated",
        )
        return self.record(plan_id, seat, native_session, reading, observed_at, expected_seats)

    def record_session_estimate(self, plan_id: int, seat: str, native_session: str, cumulative_usd: float, observed_at: float, source: str) -> UsageEstimate:
        reading = UsageReading(cumulative_usd, source, "native-session estimate", native_session, {}, "one native session", "fresh", "estimated")
        return self.record(plan_id, seat, native_session, reading, observed_at)

    def record(self, plan_id: int, seat: str, native_session: str, reading: UsageReading, observed_at: float,
               expected_seats: int | None = None) -> UsageEstimate:
        with self._lock:
            data = self._read()
            key = f"{plan_id}:{seat}"
            previous = data["seats"].get(key, {})
            native_session_id = reading.native_session_id or native_session
            reset_window_key = self.reset_window_key(reading.window)
            amount = reading.amount_usd
            if (isinstance(amount, (int, float)) and not isinstance(amount, bool)
                    and math.isfinite(float(amount)) and amount >= 0):
                previous_session = previous.get("native_session_id", previous.get("native_session"))
                same_session = previous_session == native_session_id
                legacy_window = same_session and "reset_window_key" not in previous and "native_total_usd" in previous
                same_window = previous.get("reset_window_key") == reset_window_key or legacy_window
                previous_total = float(previous.get("native_total_usd", 0.0)) if same_session and same_window else 0.0
                current_total = float(amount)
                older_sample = (same_session and same_window and reading.sampled_at is not None
                                and previous.get("sampled_at") is not None
                                and reading.sampled_at <= float(previous["sampled_at"]))
                if not older_sample:
                    reset = same_session and same_window and current_total < previous_total
                    delta = current_total if not same_session or not same_window or reset else current_total - previous_total
                    previous["estimated_usd"] = float(previous.get("estimated_usd", 0.0)) + delta
                    previous["last_estimate"] = {
                        "label": ESTIMATE_LABEL,
                        "source": reading.source or "not reported",
                        "estimate_kind": reading.estimate_kind or "unknown",
                        "native_session_id": native_session_id,
                        "worker_native_session": native_session,
                        "reset_window": reading.window,
                        "coverage": reading.coverage or "not reported",
                        "freshness": reading.freshness,
                        "status": reading.status,
                        "sampled_at": reading.sampled_at,
                    }
                    previous.update({
                        "native_session_id": native_session_id,
                        "worker_native_session": native_session,
                        "reset_window": reading.window,
                        "reset_window_key": reset_window_key,
                        "native_total_usd": current_total,
                        "sampled_at": reading.sampled_at if reading.sampled_at is not None else observed_at,
                        "first_seen": previous.get("first_seen", observed_at),
                        "last_seen": reading.sampled_at if reading.sampled_at is not None else observed_at,
                    })
            latest = {
                "label": ESTIMATE_LABEL,
                "source": reading.source or "not reported",
                "estimate_kind": reading.estimate_kind or "unknown",
                "native_session_id": native_session_id,
                "worker_native_session": native_session,
                "reset_window": reading.window,
                "coverage": reading.coverage or "not reported",
                "freshness": reading.freshness,
                "status": reading.status,
                "source_status": reading.source_status,
                "reason": reading.reason,
                "sampled_at": reading.sampled_at,
                "checked_at": observed_at,
            }
            previous.update({
                "plan_id": plan_id,
                "seat": seat,
                "latest": latest,
            })
            data["seats"][key] = previous
            self._write(data)
            return self.estimate_data(data, plan_id, observed_at, expected_seats)

    @staticmethod
    def reset_window_key(window: dict[str, object]) -> str:
        return json.dumps({key: window.get(key) for key in ("since", "resets")}, sort_keys=True)

    def estimate(self, plan_id: int, now: float, expected_seats: int | None = None) -> UsageEstimate:
        with self._lock:
            return self.estimate_data(self._read(), plan_id, now, expected_seats)

    def estimates(self, plan_ids: Iterable[int], now: float) -> dict[int, UsageEstimate]:
        with self._lock:
            data = self._read()
            return {plan_id: self.estimate_data(data, plan_id, now, None) for plan_id in sorted(set(plan_ids))}

    def seat_estimates(self, plan_id: int) -> dict[str, float | None]:
        """Recorded estimates keyed by the OpenRig seat target for one plan."""
        with self._lock:
            records = self._read()["seats"].values()
            return {
                str(row["seat"]): float(amount) if isinstance(amount, (int, float)) and not isinstance(amount, bool) and math.isfinite(float(amount)) and amount >= 0 else None
                for row in records if int(row.get("plan_id", 0)) == plan_id and row.get("seat")
                for amount in (row.get("estimated_usd"),)
            }

    def estimate_data(self, data: dict, plan_id: int, now: float, expected_seats: int | None) -> UsageEstimate:
        records = [row for row in data["seats"].values() if int(row["plan_id"]) == plan_id]
        if not records:
            coverage = f"0 of {expected_seats} seats observed" if expected_seats is not None else "0 of unknown seats observed"
            return UsageEstimate(plan_id, None, ESTIMATE_SOURCE, None, None, coverage, "missing", "missing", 0, expected_seats)
        estimated = [row for row in records if isinstance(row.get("estimated_usd"), (int, float))]
        newest = max((float(row["last_seen"]) for row in estimated), default=None)
        stale = any((row.get("latest", {}).get("freshness") == "stale"
                     or now - float(row.get("last_seen", 0)) > self.stale_after_seconds) for row in estimated)
        unavailable = any(row.get("latest", {}).get("status") == "unavailable" for row in records)
        partial = expected_seats is not None and len(estimated) < expected_seats
        coverage = (f"{len(estimated)} of {expected_seats} seats reported Estimated API cost" if expected_seats is not None
                    else f"{len(estimated)} seats reported Estimated API cost; expected count unknown")
        sources = sorted({str((row.get("last_estimate") or row.get("latest") or {}).get("source", row.get("source", "not reported"))) for row in records})
        kinds = sorted({str((row.get("last_estimate") or row.get("latest") or {}).get("estimate_kind", "OpenRig native-session estimate")) for row in records})
        source = sources[0] if len(sources) == 1 else "mixed harness sources" if sources else ESTIMATE_SOURCE
        estimate_kind = kinds[0] if len(kinds) == 1 else "mixed estimate kinds" if kinds else ""
        freshness = "stale" if stale else "unavailable" if unavailable else "fresh"
        status = ("stale" if stale else "unavailable" if unavailable else "partial" if partial
                  else "estimated" if estimated else "missing")
        return UsageEstimate(
            plan_id,
            sum(float(row["estimated_usd"]) for row in estimated) if estimated else None,
            source,
            min(float(row["first_seen"]) for row in estimated) if estimated else None,
            newest,
            coverage,
            freshness,
            status,
            len(estimated),
            expected_seats,
            estimate_kind,
            ESTIMATE_LABEL,
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

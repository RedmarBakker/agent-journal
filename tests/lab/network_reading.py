from dataclasses import dataclass
from math import ceil, isfinite
from typing import Iterable

from journal.features.organization.support.hub_traffic_audit import HubTrafficAudit, HubTrafficFinding
from tests.lab.measurement import Measurement
from tests.lab.named_measurement import NamedMeasurement
from tests.lab.reading_support import find_measurement, missing_measurements, replace_measurement, validate_measurements


NETWORK_METRICS = (
    "messages_per_edge_kind",
    "hops_per_handoff",
    "hops_per_handoff_median",
    "hops_per_handoff_p85",
    "unaccepted_handoffs",
    "uncorrelated_handoffs",
    "route_violations",
    "unresolved_route_identities",
    "handoff_latency_median_minutes",
    "handoff_latency_p85_minutes",
    "censored_handoffs",
    "handoff_rework_count",
    "handoff_rework_share",
    "censored_rework_followups",
    "escalations",
    "escalation_resolution_minutes",
    "escalation_resolution_median_minutes",
    "escalation_resolution_p85_minutes",
    "open_escalations",
    "role_queue_wait_minutes",
    "role_queue_wait_median_minutes",
    "role_queue_wait_p85_minutes",
    "pending_role_queue_wait_minutes",
    "cancelled_role_queue_jobs",
    "queue_fairness_jain",
    "domain_fan_out",
    "plan_message_share",
)


@dataclass(frozen=True)
class NetworkReading:
    measurements: tuple[NamedMeasurement, ...]

    def __post_init__(self) -> None:
        validate_measurements(self.measurements, NETWORK_METRICS, "network")

    @classmethod
    def missing(cls, reason: str, version: str) -> "NetworkReading":
        return cls(missing_measurements(NETWORK_METRICS, reason, version))

    @classmethod
    def from_hub_audit(cls, audit: HubTrafficAudit, version: str) -> "NetworkReading":
        return cls.from_findings(audit.findings(), version)

    @classmethod
    def from_findings(cls, findings: Iterable[HubTrafficFinding], version: str) -> "NetworkReading":
        reading = cls.missing("HubTrafficAudit omits unidentified sources and incomplete history", version)
        findings_by_id = {finding.item_id: finding for finding in findings}
        if not findings_by_id:
            return reading.with_measurement(
                "route_violations",
                Measurement(None, "missing", "HubTrafficAudit cannot prove zero without complete delivery-linked coverage", 0, None, (), version),
            )
        item_ids = tuple(sorted(findings_by_id))
        return reading.with_measurement(
            "route_violations",
            Measurement(
                len(item_ids),
                "partial",
                "recognized HubTrafficAudit findings; complete delivery-linked coverage is unavailable",
                len(item_ids),
                None,
                tuple(f"hub-traffic-audit:{item_id}" for item_id in item_ids),
                version,
            ),
        )

    @classmethod
    def from_simulator_observations(
        cls,
        route_latencies: Iterable[float],
        route_violations: int,
        route_attempts: int,
        expected_route_attempts: int,
        service_exposure: Iterable[tuple[int, float]],
        expected_roles: int,
        queue_waits: Iterable[float],
        expected_queue_jobs: int,
        version: str,
    ) -> "NetworkReading":
        latencies, exposures, waits = tuple(route_latencies), tuple(service_exposure), tuple(queue_waits)
        cls.validate_observations(route_violations, route_attempts, expected_route_attempts, exposures, expected_roles, waits, expected_queue_jobs)
        reading = cls.missing("the simulator supplied no complete network trace", version)
        route_refs = tuple(f"simulator:route:{index}" for index in range(route_attempts))
        route_status = cls.coverage_status(route_attempts, expected_route_attempts)
        route_reason = cls.coverage_reason(route_status, "route identities")
        reading = reading.with_measurement(
            "route_violations",
            Measurement(route_violations if route_attempts else None, route_status, route_reason, route_attempts, expected_route_attempts, route_refs, version),
        )
        latency_status = cls.coverage_status(len(latencies), route_attempts)
        if route_status != "observed" and latency_status == "observed":
            latency_status = "partial"
        reading = cls.with_samples(reading, "handoff_latency_median_minutes", latencies, 0.5, latency_status, route_reason, route_attempts, route_refs, version)
        reading = cls.with_samples(reading, "handoff_latency_p85_minutes", latencies, 0.85, latency_status, route_reason, route_attempts, route_refs, version)
        reading = cls.with_queue_samples(reading, exposures, expected_roles, waits, expected_queue_jobs, version)
        return reading

    @staticmethod
    def validate_observations(
        violations: int,
        attempts: int,
        expected_attempts: int,
        exposures: tuple[tuple[int, float], ...],
        expected_roles: int,
        waits: tuple[float, ...],
        expected_jobs: int,
    ) -> None:
        counts = (violations, attempts, expected_attempts, expected_roles, expected_jobs)
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts):
            raise ValueError("simulator metric coverage counts must be non-negative integers")
        if violations > attempts or attempts > expected_attempts or len(exposures) > expected_roles or len(waits) > expected_jobs:
            raise ValueError("simulator metric observations exceed their declared coverage")
        if any(
            not isinstance(starts, int) or isinstance(starts, bool) or starts < 0
            or isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or not isfinite(minutes) or minutes <= 0
            for starts, minutes in exposures
        ):
            raise ValueError("eligible Role exposure needs non-negative starts and positive finite minutes")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0 for value in (*waits,)):
            raise ValueError("simulated wait and latency samples must be finite non-negative numbers")

    @staticmethod
    def coverage_status(observed: int, expected: int) -> str:
        if expected == 0:
            return "not_applicable"
        if observed == 0:
            return "missing"
        return "observed" if observed == expected else "partial"

    @staticmethod
    def coverage_reason(status: str, subject: str) -> str:
        if status == "observed":
            return "complete pinned simulator coverage"
        if status == "partial":
            return f"simulator observed only part of the expected {subject}"
        if status == "not_applicable":
            return f"the scenario had no expected {subject}"
        return f"the simulator observed no {subject}"

    @classmethod
    def with_samples(
        cls,
        reading: "NetworkReading",
        name: str,
        samples: tuple[float, ...],
        percentile: float,
        status: str,
        reason: str,
        expected: int,
        references: tuple[str, ...],
        version: str,
    ) -> "NetworkReading":
        if not samples:
            if expected == 0:
                return reading.with_measurement(name, Measurement(None, "not_applicable", reason, 0, 0, (), version))
            return reading.with_measurement(name, Measurement(None, "missing", reason, 0, expected, (), version))
        status = status if status != "not_applicable" else "observed"
        value = nearest_rank(samples, percentile) if percentile != 0.5 else cls.median(samples)
        coverage_status = "observed" if status == "observed" and len(samples) == expected else "partial"
        return reading.with_measurement(name, Measurement(value, coverage_status, reason, len(samples), expected, references[:len(samples)], version))

    @staticmethod
    def median(values: tuple[float, ...]) -> float:
        ordered = sorted(values)
        middle = len(ordered) // 2
        return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2

    @classmethod
    def with_queue_samples(
        cls,
        reading: "NetworkReading",
        exposures: tuple[tuple[int, float], ...],
        expected_roles: int,
        waits: tuple[float, ...],
        expected_jobs: int,
        version: str,
    ) -> "NetworkReading":
        exposure_status = cls.coverage_status(len(exposures), expected_roles)
        exposure_refs = tuple(f"simulator:queue-role:{index}" for index in range(len(exposures)))
        rates = tuple(starts / minutes for starts, minutes in exposures)
        total, squares = sum(rates), sum(rate * rate for rate in rates)
        if expected_roles == 0:
            fairness = Measurement(None, "not_applicable", "the scenario had no eligible Role queue demand", 0, 0, (), version)
        elif exposure_status == "missing":
            fairness = Measurement(None, "missing", "eligible Role exposure was not observed", 0, expected_roles, (), version)
        elif exposure_status == "observed" and total == 0:
            fairness = Measurement(None, "not_applicable", "all eligible Roles had zero service starts", len(exposures), expected_roles, exposure_refs, version)
        else:
            status = "observed" if exposure_status == "observed" else "partial"
            value = total * total / (len(rates) * squares) if squares else 0.0
            fairness = Measurement(value, status, "Jain index of service starts per eligible backlogged minute", len(exposures), expected_roles, exposure_refs, version)
        reading = reading.with_measurement("queue_fairness_jain", fairness)
        wait_status = cls.coverage_status(len(waits), expected_jobs)
        wait_reason = cls.coverage_reason(wait_status, "queued task waits")
        references = tuple(f"simulator:queue-wait:{index}" for index in range(len(waits)))
        reading = cls.with_samples(reading, "role_queue_wait_median_minutes", waits, 0.5, wait_status, wait_reason, expected_jobs, references, version)
        return cls.with_samples(reading, "role_queue_wait_p85_minutes", waits, 0.85, wait_status, wait_reason, expected_jobs, references, version)

    def measurement(self, name: str) -> Measurement:
        return find_measurement(self.measurements, name)

    def with_measurement(self, name: str, measurement: Measurement) -> "NetworkReading":
        return NetworkReading(replace_measurement(self.measurements, name, measurement))


def nearest_rank(values: Iterable[int | float], percentile: float) -> int | float | None:
    if isinstance(percentile, bool) or not isfinite(percentile) or percentile <= 0 or percentile > 1:
        raise ValueError("percentile must be between 0 and 1")
    samples = tuple(values)
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) for value in samples):
        raise ValueError("percentile samples must be finite numbers")
    ordered = sorted(samples)
    return ordered[ceil(percentile * len(ordered)) - 1] if ordered else None

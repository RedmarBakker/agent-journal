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

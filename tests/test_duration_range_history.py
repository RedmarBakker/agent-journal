from datetime import datetime, timezone

from journal.features.estimates.support.duration_range_history import DurationRangeHistory


COHORT = {
    "environment_id": 7,
    "domain": "development",
    "size_scale_version": "points-v1",
    "criteria_version": "production-v3",
    "model": "sonnet",
    "tier": "medium",
}
AS_OF = datetime(2026, 10, 31, tzinfo=timezone.utc).timestamp()


def test_immutable_lifecycle_facts_make_separate_elapsed_execution_and_delivery_outcomes():
    histories = [{"scope": {"environment_id": 7}, "tasks": [
        task(1, [
            fact("task_started", "2026-10-01T00:00:00Z"),
            fact("task_completed", "2026-10-01T01:00:00Z"),
            fact("worker_work_merged", "2026-10-01T02:00:00Z"),
            fact("delivery_accepted", "2026-10-01T05:00:00Z", {"delivery_id": 10}),
        ], evidence_id=10),
        task(2, [
            fact("task_started", "2026-10-02T00:00:00Z"),
            fact("worker_work_merged", "2026-10-02T04:00:00Z"),
        ]),
        task(3, [fact("task_started", "2026-10-03T00:00:00Z")]),
    ]}]

    observations = DurationRangeHistory().observations(histories, AS_OF)
    by_key = {(row["task_id"], row["stage"]): row for row in observations}

    assert by_key[(1, "execution_cycle")]["duration_seconds"] == 7200
    assert by_key[(1, "delivery_delay")]["duration_seconds"] == 10800
    assert by_key[(2, "delivery_delay")]["right_censored"] is True
    assert by_key[(2, "delivery_delay")]["duration_seconds"] == AS_OF - stamp("2026-10-02T04:00:00Z")
    assert by_key[(3, "execution_cycle")]["right_censored"] is True
    assert len(observations) == 5


def task(task_id, outcomes, evidence_id=None):
    return {
        "task_id": task_id,
        "current_in_plan": True,
        "estimate_history": {"current_size": 3},
        "delivery": {"status": "delivered" if evidence_id else "awaiting_deployment", "evidence_id": evidence_id},
        "outcomes": [
            {"task_id": task_id, "kind": row[0], "occurred_at": row[1], "committed_size": 3,
             "planned_size": 3, "cohort_dimensions": COHORT, "details": row[2]}
            for row in outcomes
        ],
        "execution": {"wait_intervals": [{"kind": "review_wait", "duration_seconds": 999999}]},
    }


def fact(kind, occurred_at, details=None):
    return kind, occurred_at, details or {}


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()

from journal.features.estimates.support.baseline_forecast import BaselineForecast
from journal.repositories.delivery_forecasts import DeliveryForecasts


COHORT = {"domain": "payments", "size_scale_version": "story-points-v1", "criteria_version": "deployment-v1",
          "model": "opus", "tier": "high"}


def test_only_the_currently_accepted_delivery_generation_is_a_comparable_outcome():
    facts = [worker_fact(), delivery_fact(46, "delivery_accepted", 1), delivery_fact(47, "delivery_corrected", 2)]
    history = {"tasks": [{"task_id": 8, "delivery": {"status": "delivered", "evidence_id": 47},
                          "outcomes": facts}]}

    result = DeliveryForecasts.accepted_deliveries([history, history])

    assert result == [{"task_id": 8, "size_points": 3,
                       "cohort": {**COHORT}, "kind": "delivery_corrected", "generation": 2, "current": True}]


def test_one_delivery_record_is_one_local_day_batch_and_zero_capacity_days_are_preserved():
    dimensions = {**COHORT, "environment_id": 1}
    facts = [worker_fact(), delivery_fact(47, "delivery_accepted", 1, size=3),
             worker_fact(task_id=9), delivery_fact(47, "delivery_accepted", 1, task_id=9, size=2)]
    history = {"tasks": [{"task_id": task_id, "delivery": {"status": "delivered", "evidence_id": 47},
                          "outcomes": [row for row in facts if row.get("task_id", 8) == task_id]}
                         for task_id in (8, 9)]}
    batches = DeliveryForecasts.delivery_batches([history, history], "Europe/Amsterdam")
    report = {"days": [{"date": "2026-10-28", "availability": {"actual_places": None}},
                        {"date": "2026-10-29", "availability": {"actual_places": 0}},
                        {"date": "2026-10-30", "availability": {"actual_places": 1}}]}

    days = DeliveryForecasts.capacity_days([report], batches)
    cohort_key = BaselineForecast.cohort_key(dimensions)

    assert [row["available_places"] for row in days] == [0, 1]
    assert days[0]["deployment_batches"] == []
    assert days[1]["deployment_batches"] == [{"batch_id": "47", "points_by_cohort": {cohort_key: 5}}]


def worker_fact(task_id: int = 8) -> dict:
    return {"task_id": task_id, "kind": "worker_spent", "occurred_at": "2026-10-30T10:00:00+00:00",
            "cohort_dimensions": {"model": "opus", "tier": "high"}}


def delivery_fact(delivery_id: int, kind: str, generation: int, *, task_id: int = 8, size: int = 3) -> dict:
    dimensions = {"environment_id": 1, **COHORT, "model": None, "tier": None}
    return {"task_id": task_id, "kind": kind, "occurred_at": "2026-10-30T12:00:00+00:00",
            "committed_size": size, "planned_size": size,
            "cohort_dimensions": dimensions,
            "details": {"delivery_id": delivery_id, "generation": generation}}

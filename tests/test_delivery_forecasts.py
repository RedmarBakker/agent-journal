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


def test_capacity_freshness_uses_current_observations_and_marks_a_sprint_old_sample_stale():
    forecast = {"as_of": "2026-11-30"}
    source = {"calendar": {"sprint_length_days": 14},
              "capacity_days": [{"date": "2026-11-15", "available_places": 1},
                                {"date": "2026-12-01", "available_places": 2},
                                {"date": "2026-11-30", "available_places": True}]}

    fresh = DeliveryForecasts.capacity_freshness(forecast, {**source, "capacity_days": [{"date": "2026-11-16", "available_places": 2}]})
    stale = DeliveryForecasts.capacity_freshness(forecast, source)

    assert fresh == {"capacity_observed_through": "2026-11-16", "capacity_age_days": 14, "capacity_freshness": "fresh"}
    assert stale == {"capacity_observed_through": "2026-11-15", "capacity_age_days": 15, "capacity_freshness": "stale"}


def test_latest_delivery_time_matches_only_the_current_accepted_evidence():
    history = {"tasks": [{
        "delivery": {"evidence_id": 9},
        "outcomes": [
            {"kind": "delivery_accepted", "occurred_at": "2026-10-28T12:00:00+00:00", "details": {"delivery_id": 8}},
            {"kind": "delivery_accepted", "occurred_at": "2026-10-29T12:00:00+00:00", "details": {"delivery_id": 9}},
            {"kind": "delivery_corrected", "occurred_at": "2026-10-30T12:00:00+00:00", "details": {"delivery_id": 9}},
        ],
    }]}

    assert DeliveryForecasts.latest_delivery_at(history) == "2026-10-30T12:00:00+00:00"

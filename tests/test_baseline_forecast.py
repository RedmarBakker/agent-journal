from datetime import date, timedelta
import json

from journal.features.estimates.support.baseline_forecast import BaselineForecast


COHORT = {"domain": "payments", "size_scale_version": "story-points-v1", "criteria_version": "deployment-v1",
          "model": "opus", "tier": "high"}


def test_a_forecast_abstains_when_delivery_history_and_observed_capacity_are_missing():
    result = BaselineForecast().estimate(source(scope=[task(1, 11, 2)], deliveries=[], capacity_days=[]))

    assert result["status"] == "not enough history"
    assert result["delivered_outcomes"] == 0
    assert result["observed_capacity_days"] == 0
    assert result["missing_evidence"] == ["comparable delivery history", "observed capacity"]
    assert result["probability_this_sprint"] is None
    assert result["p50"] is None
    assert result["p85"] is None


def test_an_unknown_size_remains_in_the_recorded_scope_without_becoming_zero():
    result = BaselineForecast().estimate(source(scope=[task(1, 11, None)], deliveries=[], capacity_days=[]))

    assert result["scope"]["task_ids"] == [11]
    assert result["scope"]["remaining_size_points"] is None
    assert result["scope"]["unknown_size_tasks"] == 1


def test_sparse_delivery_history_stays_sparse_despite_many_merges():
    request = source(scope=[task(1, 11, 2)], deliveries=deliveries(2), capacity_days=capacity_days())
    request["execution_merges"] = 80

    result = BaselineForecast().estimate(request)

    assert result["status"] == "not enough history"
    assert result["delivered_outcomes"] == 2
    assert result["execution_merges"] == 80
    assert result["probability_this_sprint"] is None


def test_zero_shared_capacity_does_not_create_a_finite_finish_date():
    result = BaselineForecast().estimate(source(scope=[task(1, 11, 2)], deliveries=deliveries(10),
                                                 capacity_days=capacity_days(available_places=0, points=0)))

    assert result["status"] == "forecast"
    assert result["p50"] is None
    assert result["p85"] is None
    assert result["probability_beyond_horizon"] == 100
    assert result["bands"] == {"this_sprint": 0, "next_sprint": 0, "later": 100}
    assert result["task_forecasts"][0]["p50"] is None
    assert result["task_forecasts"][0]["probability_beyond_horizon"] == 100


def test_other_cohort_delivery_remains_in_the_shared_observed_block():
    other_cohort = {**COHORT, "domain": "operations"}
    other_key = BaselineForecast.cohort_key(other_cohort)
    rows = capacity_days(points=0)
    rows[0]["deployment_batches"] = [{"points_by_cohort": {other_key: 4}}]

    blocks, invalid = BaselineForecast.capacity_days(rows, date(2026, 10, 30))

    assert not invalid
    assert blocks[0]["deployment_batches"] == [{"points_by_cohort": {other_key: 4}}]


def test_one_deployment_batch_delivers_its_waiting_backlog_together():
    scope = [task(1, 11, 2, "awaiting_deployment"), task(2, 22, 2, "awaiting_deployment")]
    result = BaselineForecast().estimate(source(scope=scope, deliveries=deliveries(10),
                                                 capacity_days=capacity_days(points=4)))

    plans = {row["plan_id"]: row for row in result["plan_forecasts"]}
    assert result["p50"] == "2026-10-31"
    assert plans[1]["p50"] == plans[2]["p50"] == "2026-10-31"


def test_plans_share_each_sampled_delivery_block_once():
    scope = [task(1, 11, 2), task(2, 22, 2)]
    result = BaselineForecast().estimate(source(scope=scope, deliveries=deliveries(10),
                                                 capacity_days=capacity_days(points=2)))

    assert result["p50"] == "2026-11-01"
    assert result["plan_forecasts"][0]["p50"] == "2026-10-31"
    assert result["plan_forecasts"][1]["p50"] == "2026-11-01"


def test_task_p50_durations_come_from_sampled_work_intervals_in_shared_scenarios():
    scope = [task(1, 11, 2), task(1, 12, 2)]

    result = BaselineForecast().estimate(source(scope=scope, deliveries=deliveries(10),
                                                 capacity_days=capacity_days(points=2)))

    forecasts = {row["task_id"]: row for row in result["task_forecasts"]}
    assert forecasts[11]["p50"] == "2026-10-31"
    assert forecasts[11]["p85"] == "2026-10-31"
    assert forecasts[11]["p50_duration_days"] == 1
    assert forecasts[11]["p85_duration_days"] == 1
    assert forecasts[12]["p50"] == "2026-11-01"
    assert forecasts[12]["p85"] == "2026-11-01"
    assert forecasts[12]["p50_duration_days"] == 1
    assert forecasts[12]["p85_duration_days"] == 1
    plan_tasks = result["plan_forecasts"][0]["task_forecasts"]
    assert [row["task_id"] for row in plan_tasks] == [11, 12]
    assert [row["p50_duration_days"] for row in plan_tasks] == [1, 1]


def test_a_missing_next_cycle_is_named_without_inventing_its_date():
    request = source(scope=[task(1, 11, 2)], deliveries=deliveries(10), capacity_days=capacity_days(points=2))
    request["calendar"]["next_end"] = None

    result = BaselineForecast().estimate(request)

    assert result["next_status"] == "next cycle not scheduled"
    assert result["next_sprint"] is None
    assert result["probability_next_sprint"] is None
    assert result["carry_over"] == 0


def test_probability_bands_are_rounded_from_one_distribution_and_sum_to_one_hundred():
    result = BaselineForecast().estimate(source(scope=[task(1, 11, 20)], deliveries=deliveries(10),
                                                 capacity_days=capacity_days(points=2, zero_days=8)))

    assert sum(result["bands"].values()) == 100
    assert result["sensitivity"]["status"] == "observed block bootstrap"
    assert result["sensitivity"]["label"] == "Conditional range over resampled observed days; not a calibration guarantee."
    assert all(row["p10"] <= row["p90"] for row in result["sensitivity"]["bands"].values())
    assert result["method_version"] == "baseline-throughput-v2"
    assert len(result["input_cut"]) == 64
    assert result["seed"] == 43
    assert result["capacity"]["daily_observations"] == 20
    assert result["capacity"]["zero_output_days"] == 8
    assert result["scope"]["plan_ids"] == [1]


def test_an_uncertain_scope_has_no_numerical_finish_probability():
    request = source(scope=[task(1, 11, 2)], deliveries=deliveries(10), capacity_days=capacity_days())
    request["scope_uncertainties"] = [11]

    result = BaselineForecast().estimate(request)

    assert result["status"] == "unknown constraints"
    assert result["missing_evidence"] == ["approved scope"]
    assert result["unknown_constraints"] == [11]
    assert result["probability_this_sprint"] is None


def task(plan_id: int, task_id: int, points: int, delivery_status: str = "in_progress") -> dict:
    return {"plan_id": plan_id, "task_id": task_id, "cohort": COHORT, "size_points": points,
            "delivery_status": delivery_status}


def deliveries(count: int) -> list[dict]:
    return [{"task_id": 100 + index, "cohort": COHORT, "size_points": 2, "kind": "delivery_accepted"}
            for index in range(count)]


def capacity_days(points: int = 2, zero_days: int = 0, available_places: int = 1) -> list[dict]:
    cohort_key = json.dumps(COHORT, sort_keys=True, separators=(",", ":"))
    days = []
    for offset in range(20):
        has_output = offset >= zero_days and available_places > 0
        batches = [{"batch_id": f"deploy-{offset}", "points_by_cohort": {cohort_key: points}}] if has_output and points else []
        days.append({"date": (date(2026, 10, 1) + timedelta(days=offset)).isoformat(),
                     "available_places": available_places, "deployment_batches": batches})
    return days


def source(scope: list[dict], deliveries: list[dict], capacity_days: list[dict]) -> dict:
    return {"as_of": "2026-10-30", "calendar": {"current_end": "2026-11-13", "next_end": "2026-11-27",
                                                  "sprint_length_days": 14},
            "scope": scope, "accepted_deliveries": deliveries, "capacity_days": capacity_days,
            "trials": 1000, "horizon_sprints": 6, "seed": 43}

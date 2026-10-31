from datetime import date, datetime, timedelta, timezone

from journal.features.estimates.support.network_forecast import NetworkForecast


AS_OF = date(2026, 1, 1)
COHORT = "payments"


def test_serial_and_parallel_tasks_share_trials_and_compare_with_the_baseline():
    source = network_source([
        task(1, 1),
        task(2, 1),
        task(3, 2),
    ], edges=[edge(2, 1)], capacity=2)

    forecast = NetworkForecast().estimate(source, {"status": "forecast", "p50": "2026-01-02", "p85": "2026-01-03"})

    plans = {row["plan_id"]: row for row in forecast["plan_forecasts"]}
    assert forecast["status"] == "forecast"
    assert plans[1]["p50"] == "2026-01-03"
    assert plans[2]["p50"] == "2026-01-02"
    assert forecast["comparison"]["baseline"]["p50"] == "2026-01-02"
    assert forecast["comparison"]["selection"] == "none"
    assert forecast["uncertainty"]["monte_carlo"]["trials"] == 1
    assert "history" in forecast["uncertainty"]


def test_cross_domain_work_shares_execution_places_without_overbooking():
    first, second = task(1, 1, "payments"), task(2, 2, "identity")
    source = network_source([first, second], capacity=1)

    forecast = NetworkForecast().estimate(source, {"status": "not enough history"})

    plans = {row["plan_id"]: row for row in forecast["plan_forecasts"]}
    assert plans[1]["p50"] == "2026-01-02"
    assert plans[2]["p50"] == "2026-01-03"
    assert forecast["diagnostics"]["maximum_execution_wip"] == 1


def test_one_shared_deployment_batch_limits_tasks_across_plans_without_adding_delay_twice():
    tasks = [task(1, 1, execution=0, delivery=2), task(2, 2, execution=0, delivery=2)]
    source = network_source(tasks, capacity=2, batch_points=1)

    forecast = NetworkForecast().estimate(source, {"status": "not enough history"})

    by_task = {row["task_id"]: row for row in forecast["task_forecasts"]}
    assert by_task[1]["p50"] == "2026-01-03"
    assert by_task[2]["p50"] == "2026-01-04"
    assert by_task[1]["criticality_probability"] == 100
    assert by_task[2]["criticality_probability"] == 100
    assert forecast["diagnostics"]["deployment_batches_used"] == 2


def test_execution_and_delivery_residuals_are_conditioned_on_each_current_age():
    tasks = [
        task(1, 1, execution=4, age_days=3),
        task(2, 1, execution=4),
        task(3, 2, execution=4, delivery=4, stage="delivery_delay", age_days=3),
        task(4, 2, execution=4, delivery=4, stage="delivery_delay"),
    ]
    source = network_source(tasks, capacity=4)

    forecast = NetworkForecast().estimate(source, {"status": "not enough history"})

    by_task = {row["task_id"]: row for row in forecast["task_forecasts"]}
    assert by_task[1]["p50"] == "2026-01-02"
    assert by_task[2]["p50"] == "2026-01-05"
    assert by_task[3]["p50"] == "2026-01-02"
    assert by_task[4]["p50"] == "2026-01-05"


def test_execution_plan_and_domain_wip_limits_apply_to_new_starts():
    execution = network_source([task(1, 1), task(2, 2)], capacity=2)
    execution["wip_limits"]["execution"] = 1
    execution_forecast = NetworkForecast().estimate(execution, {"status": "not enough history"})

    plan = network_source([task(1, 1, execution=1, delivery=2), task(2, 1, execution=1, delivery=2)], capacity=2)
    plan["wip_limits"]["plan_delivery"] = 1
    plan_forecast = NetworkForecast().estimate(plan, {"status": "not enough history"})

    domain = network_source([task(1, 1, execution=1, delivery=2), task(2, 2, execution=1, delivery=2)], capacity=2)
    domain["wip_limits"]["domain_delivery"] = 1
    domain_forecast = NetworkForecast().estimate(domain, {"status": "not enough history"})

    execution_plans = {row["plan_id"]: row for row in execution_forecast["plan_forecasts"]}
    plan_result = plan_forecast["plan_forecasts"][0]
    domain_plans = {row["plan_id"]: row for row in domain_forecast["plan_forecasts"]}
    assert execution_forecast["diagnostics"]["maximum_execution_wip"] == 1
    assert execution_plans[2]["p50"] == "2026-01-03"
    assert plan_result["p50"] == "2026-01-07"
    assert plan_forecast["diagnostics"]["maximum_plan_delivery_wip"] == 1
    assert domain_plans[2]["p50"] == "2026-01-07"
    assert domain_forecast["diagnostics"]["maximum_domain_delivery_wip"] == 1


def test_worker_assignment_ceiling_limits_queued_and_current_work():
    tasks = [task(1, 1, execution=2, delivery=2), task(2, 1, execution=1)]
    limited = network_source(tasks, capacity=1)
    limited["wip_limits"]["worker_queue"] = 1
    unlimited = network_source(tasks, capacity=1)

    limited_forecast = NetworkForecast().estimate(limited, {"status": "not enough history"})
    unlimited_forecast = NetworkForecast().estimate(unlimited, {"status": "not enough history"})

    limited_tasks = {row["task_id"]: row for row in limited_forecast["task_forecasts"]}
    unlimited_tasks = {row["task_id"]: row for row in unlimited_forecast["task_forecasts"]}
    assert limited_tasks[2]["p50"] == "2026-01-04"
    assert unlimited_tasks[2]["p50"] == "2026-01-04"
    assert limited_forecast["diagnostics"]["maximum_worker_queue_wip"] == 1
    assert unlimited_forecast["diagnostics"]["maximum_worker_queue_wip"] == 2


def test_worker_queue_uses_the_shared_critical_slack_order():
    source = network_source([task(1, 1), task(2, 1)], capacity=1)
    source["wip_limits"]["worker_queue"] = 1
    source["ready_forecasts"] = {"1": {"probability_this_sprint": 50, "sprint": {"ends_on": "2026-01-04"},
                                       "critical_path": {"tasks": [{"task_id": 1, "slack_days": 2},
                                                                       {"task_id": 2, "slack_days": 0}]}}}

    forecast = NetworkForecast().estimate(source, {"status": "not enough history"})

    by_task = {row["task_id"]: row for row in forecast["task_forecasts"]}
    assert by_task[2]["p50"] == "2026-01-02"
    assert by_task[1]["p50"] == "2026-01-03"


def test_existing_execution_uses_a_place_before_new_work_can_start():
    tasks = [task(1, 1), task(2, 1)]
    states = NetworkForecast.initial_states(tasks, {
        1: {"execution_cycle": 1, "delivery_delay": 0},
        2: {"execution_cycle": 1, "delivery_delay": 0},
    })
    states[2]["started"] = True
    states[2]["execution_start"] = 0
    queues = [[1], [2]]
    resource_edges = []

    NetworkForecast().start_queued(
        tasks, states, queues, {}, {"mode": "off", "wip_limits": {}}, 0, 1, resource_edges, [None, None],
    )

    assert states[1]["started"] is False
    assert states[2]["started"] is True


def test_unresolved_external_gates_and_zero_capacity_are_bounded_explicitly():
    edge_row = {**edge(2, 900), "external": True}
    external = network_source([task(2, 1)], edges=[edge_row], capacity=1)
    external["graph"]["external_conditions"] = [{**edge_row, "status": "unresolved"}]

    gated = NetworkForecast().estimate(external, {"status": "not enough history"})

    assert gated["status"] == "unknown constraints"
    assert gated["p50"] is None
    assert gated["external_conditions"] == [{**edge_row, "status": "unresolved"}]

    stopped = NetworkForecast().estimate(network_source([task(1, 1)], capacity=0), {"status": "forecast"})

    assert stopped["status"] == "zero capacity"
    assert stopped["p50"] is None
    assert stopped["probability_beyond_horizon"] == 100
    assert stopped["uncertainty"]["monte_carlo"]["probability_standard_error_pct"] == 0


def test_missing_delivery_capacity_and_invalid_horizon_are_explicit():
    missing_batch = network_source([task(1, 1)], capacity=1)
    for block in missing_batch["capacity_days"]:
        block["deployment_batches"] = []
    no_batch_forecast = NetworkForecast().estimate(missing_batch, {"status": "forecast"})

    invalid_horizon = network_source([task(1, 1)], capacity=1)
    invalid_horizon["horizon_days"] = 0
    horizon_forecast = NetworkForecast().estimate(invalid_horizon, {"status": "forecast"})

    no_capacity = network_source([task(1, 1)], capacity=1)
    no_capacity["capacity_days"] = []
    no_capacity_forecast = NetworkForecast().estimate(no_capacity, {"status": "forecast"})

    assert no_batch_forecast["status"] == "not enough history"
    assert "task 1 shared delivery capacity" in no_batch_forecast["missing_evidence"]
    assert horizon_forecast["status"] == "not enough history"
    assert "bounded simulation horizon" in horizon_forecast["missing_evidence"]
    assert no_capacity_forecast["status"] == "not enough history"
    assert "observed shared capacity" in no_capacity_forecast["missing_evidence"]


def test_future_capacity_rows_are_not_sampled_as_observed_history():
    source = network_source([task(1, 1)], capacity=1)
    source["capacity_days"].append({"date": (AS_OF + timedelta(days=1)).isoformat(),
                                    "available_places": 99,
                                    "deployment_batches": [{"points_by_cohort": {COHORT: 99}}]})

    forecast = NetworkForecast().estimate(source, {"status": "forecast"})

    assert forecast["status"] == "not enough history"
    assert forecast["capacity_days_used"] == 4
    assert "valid shared capacity records" in forecast["missing_evidence"]


def network_source(tasks, *, edges=(), capacity=2, batch_points=20):
    block = {"available_places": capacity, "deployment_batches": [
        {"batch_id": "release", "points_by_cohort": {COHORT: batch_points, "identity": batch_points}}
    ]}
    return {
        "as_of": AS_OF.isoformat(), "trials": 1, "seed": 41, "horizon_days": 8,
        "calendar": {"current_end": "2026-01-04", "next_end": "2026-01-08"},
        "scope": tasks, "graph": {"edges": list(edges), "external_conditions": []},
        "capacity_days": [{"date": (AS_OF - timedelta(days=offset)).isoformat(), **block}
                          for offset in range(1, 5)],
        "wip_limits": {"execution": 0, "worker_queue": 0, "plan_delivery": 0, "domain_delivery": 0},
    }


def task(task_id, plan_id, domain=COHORT, *, execution=1, delivery=0, stage="execution_cycle", age_days=0):
    return {
        "task_id": task_id, "plan_id": plan_id, "plan_ids": [plan_id], "domain": domain,
        "cohort_key": domain, "size_points": 1, "priority": 50,
        "created_at": datetime(2025, 12, 1, tzinfo=timezone.utc),
        "current_stage": stage, "age_seconds": age_days * 86400, "started": stage == "delivery_delay" or age_days > 0,
        "stages": {
            "execution_cycle": duration(execution), "delivery_delay": duration(delivery),
        },
    }


def duration(days):
    seconds = days * 86400
    return {"status": "forecast", "p50_seconds": seconds, "p85_seconds": seconds,
            "completed_samples": 3, "censored_samples": 0, "effective_sample_count": 3.0,
            "limitations": []}


def edge(task_id, prerequisite_id, kind="prerequisite"):
    return {"task_id": task_id, "prerequisite_id": prerequisite_id, "kind": kind, "external": False}

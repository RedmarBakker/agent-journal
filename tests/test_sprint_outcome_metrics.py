from journal.repositories.sprint_outcome_metrics import SprintOutcomeMetrics


def test_a_fixed_sprint_replays_its_committed_scope_and_credits_delivery_when_recorded():
    report = SprintOutcomeMetrics.project(fixed_sprint(), fixed_histories())

    assert report["scope"]["baseline"]["task_ids"] == [11, 12, 14]
    assert report["scope"]["baseline"]["known_size_points"] == 8
    assert report["scope"]["baseline"]["unknown_size_tasks"] == 1
    assert report["scope"]["added"]["task_ids"] == [13]
    assert report["scope"]["removed"]["task_ids"] == [14]

    by_date = {day["date"]: day for day in report["days"]}
    assert by_date["2026-10-29"]["delivered"][0]["size_points"] == 0
    assert by_date["2026-10-29"]["remaining"][0]["size_points"] == 8
    assert by_date["2026-10-31"]["delivered"][0]["size_points"] == 3
    remaining = {row["domain"]: row["size_points"] for row in by_date["2026-10-31"]["remaining"]}
    assert remaining == {"development": 5, "operations": 2}
    development_flow = next(row for row in by_date["2026-10-31"]["cumulative_flow"] if row["domain"] == "development")
    assert development_flow["awaiting_deployment"] == 1
    assert development_flow["delivered"] == 1
    assert by_date["2026-11-01"]["remaining"][0]["unknown_size_tasks"] == 0
    executed = {row["model"]: row["size_points"] for row in report["throughput"]["execution"]}
    assert executed == {"model-a": 3, "model-b": 5}
    assert report["throughput"]["delivered"][0]["size_points"] == 3
    assert report["velocity"]["status"] == "closed"
    assert report["velocity"]["by_cohort"][0]["size_points"] == 3

    ranges = {(row["domain"], row["size_points"]): row for row in report["ranges_by_size"]}
    assert ranges[("development", 3)]["cycle_time_seconds"] == {"minimum": 90000, "maximum": 90000, "samples": 1}
    assert ranges[("development", 3)]["delivery_wait_seconds"] == {"minimum": 259200, "maximum": 259200, "samples": 1, "right_censored_tasks": 0}
    assert ranges[("development", 5)]["delivery_wait_seconds"]["right_censored_tasks"] == 1


def test_an_open_sprint_does_not_call_an_unobserved_empty_day_zero_output():
    report = SprintOutcomeMetrics.project(open_sprint(), [])

    assert report["velocity"] == {"status": "in_progress", "by_cohort": None}
    assert report["availability"] == {"status": "not_measured", "daily_observations": None}
    assert report["days"][0]["availability"] == {"status": "not_measured", "available_places": None, "actual_places": None}
    assert report["days"][0]["zero_output"] is None


def fixed_sprint() -> dict:
    return {"id": 7, "starts_on": "2026-10-26", "ends_on": "2026-11-09", "starts_at": "2026-10-26T00:00:00+00:00",
            "ends_at": "2026-11-09T00:00:00+00:00", "timezone": "UTC", "length_days": 14, "state": "closed",
            "commitments": [{"plan_id": 1, "tasks": [snapshot(11, "development", 3, "scale-a", "done-a"),
                                                          snapshot(12, "development", 5, "scale-a", "done-a"),
                                                          snapshot(14, "development", None, "scale-a", "done-a")]}],
            "changes": [{"change_type": "plan_added", "plan_id": 2, "reason": "expanded delivery", "actor": "user:1",
                         "created_at": "2026-10-30T09:00:00+00:00",
                         "data": {"tasks": [snapshot(13, "operations", 2, "scale-b", "done-b")]}}]}


def open_sprint() -> dict:
    sprint = fixed_sprint()
    return {**sprint, "state": "active", "commitments": [], "changes": []}


def snapshot(task_id: int, domain: str, size: int | None, scale: str, criteria: str) -> dict:
    return {"id": task_id, "title": f"task {task_id}", "domain": domain, "size": size,
            "size_scale_version": scale, "criteria_version": criteria,
            "definition_of_done": {"evidence": "production_deployment"} if domain == "development" else None}


def fixed_histories() -> list[dict]:
    return [{"scope": {"plan_id": 1}, "tasks": [
        task(11, [fact("task_started", "2026-10-27T09:00:00+00:00", model="model-a", tier="high"),
                  fact("worker_work_merged", "2026-10-28T10:00:00+00:00", model="model-a", tier="high", committed_size=8),
                  fact("delivery_accepted", "2026-10-31T10:00:00+00:00", occurred="2026-10-29T10:00:00+00:00", model="model-a", tier="high"),
                  fact("delivery_corrected", "2026-10-31T11:00:00+00:00", model="model-a", tier="high")], "delivered"),
        task(12, [fact("task_started", "2026-10-27T09:00:00+00:00", model="model-b", tier="standard"),
                  fact("worker_work_merged", "2026-10-28T10:00:00+00:00", model="model-b", tier="standard")], "awaiting_deployment"),
        task(14, [fact("task_cancelled", "2026-11-01T12:00:00+00:00", reason="removed from scope")], "unknown")]},
        {"scope": {"plan_id": 2}, "tasks": [task(13, [], "unknown")] }]


def task(task_id: int, outcomes: list[dict], delivery: str) -> dict:
    return {"task_id": task_id, "title": f"task {task_id}", "current_in_plan": True,
            "estimate_history": {"history": []}, "delivery": {"status": delivery}, "outcomes": outcomes}


def fact(kind: str, recorded_at: str, *, occurred: str | None = None, model: str | None = None,
         tier: str | None = None, committed_size: int | None = None, reason: str = "") -> dict:
    dimensions = {"model": model, "tier": tier} if model else None
    return {"kind": kind, "recorded_at": recorded_at, "occurred_at": occurred or recorded_at,
            "cohort_dimensions": dimensions, "committed_size": committed_size, "details": {"reason": reason}}

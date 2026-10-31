from journal.features.estimates.support.critical_path import CriticalPath


def test_serial_chain_and_parallel_task_have_consistent_earliest_dates_and_slack():
    graph = CriticalPath().project(
        "2026-10-30",
        [task(1, 2), task(2, 3), task(3, 1), task(4, 4)],
        {"edges": [prerequisite(2, 1), prerequisite(3, 2)], "external_conditions": []},
    )

    assert graph["status"] == "estimated"
    assert graph["p50_finish"] == "2026-11-05"
    assert graph["critical_path_task_ids"] == [1, 2, 3]
    assert graph["independent_groups"] == [[4]]
    rows = {row["task_id"]: row for row in graph["tasks"]}
    assert rows[1]["earliest_start"] == "2026-10-30"
    assert rows[2]["earliest_start"] == "2026-11-01"
    assert rows[3]["earliest_finish"] == "2026-11-05"
    assert rows[4]["slack_days"] == 2
    assert rows[4]["critical"] is False


def test_shared_delivery_gate_is_counted_once_before_parallel_tasks():
    graph = CriticalPath().project(
        "2026-10-30",
        [task(90, 2), task(91, 6), task(92, 3), task(93, 4)],
        {"edges": [delivery_gate(92, 90), delivery_gate(93, 90)], "external_conditions": []},
    )

    assert graph["p50_finish"] == "2026-11-05"
    assert graph["critical_path_task_ids"] == [90, 93]
    assert graph["critical_task_ids"] == [90, 91, 93]
    assert graph["independent_groups"] == [[91]]
    assert graph["edges"] == [
        {"task_id": 92, "prerequisite_id": 90, "kind": "delivery_gate", "external": False},
        {"task_id": 93, "prerequisite_id": 90, "kind": "delivery_gate", "external": False},
    ]
    rows = {row["task_id"]: row for row in graph["tasks"]}
    assert rows[92]["earliest_start"] == rows[93]["earliest_start"] == "2026-11-01"
    assert rows[92]["slack_days"] == 1


def test_cross_plan_delivery_gate_is_shown_as_unresolved_without_a_fake_date():
    edge = {"task_id": 92, "prerequisite_id": 900, "kind": "delivery_gate", "external": True}
    graph = CriticalPath().project(
        "2026-10-30",
        [task(92, 3)],
        {"edges": [edge], "external_conditions": [{**edge, "status": "unresolved"}]},
    )

    assert graph["status"] == "structural"
    assert graph["basis"] == "structural dependency graph"
    assert graph["p50_finish"] is None
    assert graph["edges"] == [edge]
    assert graph["external_conditions"] == [{**edge, "status": "unresolved"}]
    assert graph["tasks"][0]["earliest_start"] is None
    assert graph["tasks"][0]["slack_days"] is None


def test_missing_task_duration_keeps_the_graph_structural_and_dates_unknown():
    graph = CriticalPath().project(
        "2026-10-30",
        [task(1, None)],
        {"edges": [], "external_conditions": []},
    )

    assert graph["status"] == "structural"
    assert graph["p50_finish"] is None
    assert graph["critical_path_task_ids"] == []
    assert graph["tasks"][0]["p50_duration_days"] is None
    assert graph["tasks"][0]["earliest_start"] is None
    assert graph["tasks"][0]["earliest_finish"] is None
    assert graph["tasks"][0]["slack_days"] is None


def task(task_id, duration):
    return {"task_id": task_id, "p50_duration_days": duration}


def prerequisite(task_id, prerequisite_id):
    return {"task_id": task_id, "prerequisite_id": prerequisite_id, "kind": "prerequisite"}


def delivery_gate(task_id, prerequisite_id):
    return {"task_id": task_id, "prerequisite_id": prerequisite_id, "kind": "delivery_gate"}

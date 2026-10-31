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


def test_composition_examples_keep_original_sizes_and_exclude_unaccepted_or_out_of_scope_work():
    matching = task(1, [
        fact("task_started", "2026-10-01T00:00:00Z"),
        fact("task_completed", "2026-10-01T01:00:00Z"),
        fact("delivery_accepted", "2026-10-01T03:00:00Z", {"delivery_id": 11}),
    ], evidence_id=11)
    matching["title"] = "production release"
    matching["estimate_history"]["planning_baseline_size"] = 5
    wrong_environment = {**matching, "task_id": 2,
                        "estimate_history": {**matching["estimate_history"], "planning_baseline_size": 8},
                        "delivery": {"status": "delivered", "evidence_id": 12},
                        "outcomes": [{**row, "task_id": 2,
                                      "cohort_dimensions": {**COHORT, "environment_id": 8},
                                      "details": {"delivery_id": 12} if row["kind"] == "delivery_accepted" else row["details"]}
                                     for row in matching["outcomes"]]}
    current_task = {**matching, "task_id": 3, "title": "current composition",
                    "outcomes": [{**row, "task_id": 3} for row in matching["outcomes"]]}
    unfinished = {**matching, "task_id": 4, "delivery": {"status": "awaiting deployment", "evidence_id": None},
                  "outcomes": [{**row, "task_id": 4} for row in matching["outcomes"]]}

    result = DurationRangeHistory().examples(
        [{"scope": {"environment_id": 7, "plan_id": 1}, "tasks": [
            matching, current_task, unfinished, wrong_environment,
        ]}],
        COHORT, exclude_task_id=3, as_of=AS_OF,
    )

    assert result == [{"task_id": 1, "plan_id": 1, "title": "production release", "original_size_points": 5,
                      "execution_size_points": 3, "execution_seconds": 3600, "delivery_seconds": 7200}]


def test_duration_history_freshness_uses_the_latest_uncensored_outcome_and_model_half_life():
    result = DurationRangeHistory.freshness([
        {"observed_at": AS_OF - 181 * 86400, "right_censored": False, "cohort_changed": False},
        {"observed_at": AS_OF, "right_censored": True, "cohort_changed": False},
        {"observed_at": AS_OF - 200 * 86400, "right_censored": False, "cohort_changed": True},
    ], AS_OF)

    assert result == {"completed_observations": 1, "observed_through": "2026-05-03", "age_days": 181,
                      "freshness": "stale", "recency_half_life_days": 180}


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

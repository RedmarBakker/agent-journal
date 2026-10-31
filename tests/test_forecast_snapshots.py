from datetime import datetime, timezone

import pytest

from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.delivery_forecasts import DeliveryForecasts
from journal.repositories.forecast_snapshots import ForecastSnapshots
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


def test_numerical_forecast_inputs_are_saved_once_per_scope_and_cut(app):
    owner = Actor.user(1)
    with app.container.get(Scope).environment(1):
        plan = app.container.get(Plans).save(Plan(title="release"), owner)
        snapshots = app.container.get(ForecastSnapshots)
        source = {"scope": [{"task_id": 7, "size_points": 3}]}
        forecast = {"status": "forecast", "input_cut": "cut-a", "as_of": "2026-10-30",
                    "seed": 43, "method_version": "baseline-throughput-v1"}

        first = snapshots.capture(plan, source, forecast, owner)
        replay = snapshots.capture(plan, source, forecast, owner)
        revised = snapshots.capture(plan, {"scope": [{"task_id": 7, "size_points": 5}]},
                                    {**forecast, "input_cut": "cut-b"}, owner)

        rows = snapshots.for_scope(plan)
        assert first["forecast_snapshot_id"] == replay["forecast_snapshot_id"]
        assert revised["forecast_snapshot_id"] != first["forecast_snapshot_id"]
        assert [row.data["input_snapshot"] for row in rows] == [source, {"scope": [{"task_id": 7, "size_points": 5}]}]
        with pytest.raises(Rejection, match="forecast snapshots are immutable"):
            snapshots.save(rows[0].with_(input_cut="rewritten"), owner)
        with pytest.raises(Rejection, match="forecast snapshots are immutable"):
            snapshots.delete(rows[0], owner)


def test_abstentions_do_not_become_out_of_sample_forecast_records(app):
    owner = Actor.user(1)
    with app.container.get(Scope).environment(1):
        plan = app.container.get(Plans).save(Plan(title="release"), owner)
        snapshots = app.container.get(ForecastSnapshots)

        result = snapshots.capture(plan, {"scope": []}, {"status": "not enough history"}, owner)

        assert result == {"status": "not enough history"}
        assert snapshots.for_scope(plan) == []


def test_saved_duration_ranges_are_frozen_even_when_shared_capacity_is_missing(app):
    owner = Actor.user(1)
    with app.container.get(Scope).environment(1):
        plan = app.container.get(Plans).save(Plan(title="release"), owner)
        snapshots = app.container.get(ForecastSnapshots)
        source = {"duration_observations": [{"task_id": 1, "duration_seconds": 600}]}
        forecast = {"status": "not enough history", "input_cut": "cut-a", "as_of": "2026-10-30",
                    "seed": 43, "method_version": "baseline-throughput-v1",
                    "duration_ranges": {"status": "forecast", "input_cut": "range-cut",
                                        "method_version": "bayesian-log-linear-duration-v1", "tasks": []}}

        first = snapshots.capture(plan, source, forecast, owner)
        replay = snapshots.capture(plan, source, forecast, owner)
        rows = snapshots.for_scope(plan)

        assert first["forecast_snapshot_id"] == replay["forecast_snapshot_id"]
        assert len(rows) == 1
        assert rows[0].data["forecast"]["duration_ranges"] == forecast["duration_ranges"]


def test_delivery_forecast_exposes_learned_ranges_from_immutable_outcome_history(app):
    owner = Actor.user(1)
    with app.container.get(Scope).environment(1):
        plan = app.container.get(Plans).save(Plan(title="release"), owner)
        task = app.container.get(Tasks).save(Task(environment_id=1, title="deployment", size=3), owner)
        app.container.get(Links).linked(Ref.build(task), Ref.build(plan), PLAN_LINK, owner)
        time_source = app.container.get(TimeSource)
        as_of = time_source.seconds()
        cohort = {"environment_id": 1, "domain": "development", "size_scale_version": "points-v1",
                  "criteria_version": "production-v3", "model": "sonnet", "tier": "medium",
                  "cohort_version": "plan4-outcome-cohort-v1"}
        historical_tasks = [completed_history(index, as_of, cohort) for index in range(12)]
        candidate = {"task_id": task.row_id, "current_in_plan": True,
                     "estimate_history": {"current_size": 3, "current_scale_version": "points-v1"},
                     "delivery": {"domain": "development", "criteria_version": "production-v3"},
                     "outcomes": [], "execution": {}}
        histories = [{"scope": {"environment_id": 1, "plan_id": plan.row_id},
                      "tasks": [*historical_tasks, candidate]}]
        source = {"scope": [{"plan_id": plan.row_id, "task_id": task.row_id, "size_points": 3, "cohort": cohort}]}

        forecast = app.container.get(DeliveryForecasts).with_duration_ranges(
            {"status": "not_enough_history"}, source, [plan], histories, plan.row_id)

        assert forecast["duration_ranges"]["status"] == "forecast"
        assert forecast["duration_ranges"]["method_version"] == "bayesian-log-linear-duration-v1"
        assert forecast["duration_ranges"]["input_cut"]
        assert forecast["duration_ranges"]["tasks"][0]["task_id"] == task.row_id
        assert forecast["duration_ranges"]["tasks"][0]["stages"]["execution_cycle"]["status"] == "forecast"
        assert forecast["duration_calibration"]["status"] == "not_enough_history"


def completed_history(index, as_of, cohort):
    start = as_of - (index + 2) * 86400
    size = (1, 2, 3, 5, 8, 13)[index % 6]
    end = start + size * 3600
    return {"task_id": index + 100, "outcomes": [
        outcome("task_started", start, cohort, size),
        outcome("task_completed", end, cohort, size),
    ]}


def outcome(kind, moment, cohort, size):
    return {"kind": kind, "occurred_at": datetime.fromtimestamp(moment, timezone.utc).isoformat(),
            "cohort_dimensions": cohort, "cohort_version": "plan4-outcome-cohort-v1", "committed_size": size}

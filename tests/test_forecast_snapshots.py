import pytest

from journal.models.plan import Plan
from journal.repositories.forecast_snapshots import ForecastSnapshots
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.rejection import Rejection


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

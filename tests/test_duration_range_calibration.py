from journal.features.estimates.support.duration_range_calibration import DurationRangeCalibration
from journal.models.forecast_snapshot import ForecastSnapshot


COHORT = {"environment_id": 7, "domain": "development", "size_scale_version": "points-v1",
          "criteria_version": "production-v3", "model": "sonnet", "tier": "medium"}


def test_rolling_origin_calibration_uses_only_saved_predictions_and_past_outcomes():
    forecasts = [
        forecast(1, 10, "cut-1", 100, 120),
        forecast(2, 60, "cut-2", 100, 120),
        forecast(3, 120, "cut-3", 100, 120),
    ]
    outcomes = [
        observation(1, 50, 300),
        observation(2, 70, 300),
        observation(3, 150, 300),
    ]

    result = DurationRangeCalibration(minimum_calibration_samples=1).replay(forecasts, outcomes, 200)
    by_id = {row["task_id"]: row for row in result["predictions"]}

    assert by_id[1]["calibration_samples"] == 0
    assert by_id[2]["calibration_samples"] == 1
    assert by_id[2]["calibrated_p85_seconds"] >= 300
    assert by_id[2]["input_cut"] == "cut-2"
    assert by_id[3]["calibration_samples"] == 2
    assert result["coverage"]["p50"] == {"covered": 0, "observed": 3, "percent": 0}
    assert result["coverage"]["raw_p85"]["observed"] == 3
    assert result["label"] == "Observed held-out coverage; nominal P85 is a target, not a guarantee."


def test_censored_outcomes_are_reported_but_do_not_count_as_coverage():
    result = DurationRangeCalibration().replay(
        [forecast(1, 10, "cut-1", 100, 200)],
        [observation(1, 50, 300, right_censored=True)],
        100,
    )

    assert result["status"] == "not_enough_history"
    assert result["coverage"]["raw_p85"]["observed"] == 0
    assert result["censored_predictions"] == 1
    assert result["drift"]["status"] == "not_enough_history"


def test_aggregate_sizing_bias_waits_for_the_minimum_held_out_actuals():
    forecasts = [forecast(index, index * 100, f"cut-{index}", 100, 200) for index in range(1, 6)]
    outcomes = [observation(index, index * 100 + 50, 200) for index in range(1, 6)]

    measured = DurationRangeCalibration().replay(forecasts, outcomes, 1000)
    sparse = DurationRangeCalibration().replay(forecasts[:4], outcomes[:4], 1000)

    assert measured["sizing_bias"]["execution_cycle"] == {
        "status": "measured", "observed": 5, "actual_to_predicted_p50_ratio": 2.0,
    }
    assert sparse["sizing_bias"]["execution_cycle"] == {
        "status": "not_enough_history", "observed": 4, "actual_to_predicted_p50_ratio": None,
    }


def test_observed_coverage_and_recent_residual_drift_are_reported():
    forecasts = [forecast(index, index * 100, f"cut-{index}", 100, 120) for index in range(1, 7)]
    outcomes = [observation(index, index * 100 + 50, 100 if index < 4 else 400) for index in range(1, 7)]

    result = DurationRangeCalibration(minimum_calibration_samples=2, minimum_drift_samples=2).replay(forecasts, outcomes, 1000)

    assert result["status"] == "measured"
    assert result["coverage"]["p50"]["observed"] == 6
    assert result["coverage"]["raw_p85"]["percent"] == 50
    assert result["drift"]["status"] == "measured"
    assert result["drift"]["recent_to_earlier_residual_ratio"] > 1


def test_rolling_origin_compares_saved_ranges_with_a_past_only_empirical_baseline():
    forecasts = [forecast(index, index * 100, f"cut-{index}", 100, 120) for index in range(1, 6)]
    outcomes = [observation(index, index * 100 + 50, 300 if index < 3 else 1000) for index in range(1, 6)]

    result = DurationRangeCalibration().replay(forecasts, outcomes, 1000)
    by_id = {row["task_id"]: row for row in result["predictions"]}

    assert by_id[1]["empirical_samples"] == 0
    assert by_id[3]["empirical_samples"] == 2
    assert by_id[4]["empirical_samples"] == 3
    assert abs(by_id[4]["empirical_p50_seconds"] - 300) < 0.001
    assert by_id[4]["actual_at"] == 450
    assert result["coverage"]["empirical_p50"]["observed"] == 2
    assert result["coverage"]["empirical_p85"]["observed"] == 2


def test_calibration_reads_only_the_frozen_duration_ranges_in_saved_forecast_snapshots():
    snapshot = ForecastSnapshot(id=10, captured_at=10, input_cut="snapshot-cut", method_version="baseline-v1",
                                data={"forecast": {"duration_ranges": {"status": "forecast", "input_cut": "range-cut",
                                    "method_version": "duration-v1", "tasks": [{"task_id": 1, "cohort": COHORT,
                                    "size_points": 3, "stages": {"execution_cycle": {"status": "forecast",
                                    "p50_seconds": 100, "p85_seconds": 200}}}]}}})

    result = DurationRangeCalibration().replay([snapshot], [observation(1, 50, 150)], 100)

    assert result["prediction_count"] == 1
    assert result["predictions"][0]["input_cut"] == "range-cut"
    assert result["coverage"]["raw_p85"]["covered"] == 1


def forecast(task_id, captured_at, input_cut, p50, p85):
    return {"task_id": task_id, "stage": "execution_cycle", "cohort": COHORT, "size_points": 3,
            "captured_at": captured_at, "input_cut": input_cut, "method_version": "duration-v1",
            "p50_seconds": p50, "p85_seconds": p85}


def observation(task_id, observed_at, duration, right_censored=False):
    return {"task_id": task_id, "stage": "execution_cycle", "cohort": COHORT,
            "size_points": 3, "observed_at": observed_at, "duration_seconds": duration,
            "right_censored": right_censored}

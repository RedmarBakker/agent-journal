from journal.features.estimates.support.estimates_forecast import EstimatesForecast


def test_builder_duration_ranges_explain_a_typical_and_wider_time():
    result = EstimatesForecast.duration_lines({
        "size_points": 5,
        "stages": {"execution_cycle": {"status": "forecast", "p50_seconds": 3600, "p85_seconds": 7200}},
    })

    assert result == ["For 5 points, work is estimated at 1.0 hours for a typical task and up to 2.0 hours in the wider range."]


def test_builder_examples_name_the_original_size_and_actual_times():
    result = EstimatesForecast.example_line({"task_id": 12, "original_size_points": 3,
                                               "execution_size_points": 5, "execution_seconds": 3600,
                                               "delivery_seconds": 7200})

    assert result == "Task 12 · original estimate 3 points · final size 5 points · work took 1.0 hours · delivery took 2.0 hours after work finished"


def test_builder_explains_when_there_are_not_enough_finished_tasks_to_compare():
    result = EstimatesForecast.bias_lines({"minimum_calibration_samples": 5, "sizing_bias": {
        "execution_cycle": {"status": "not_enough_history", "observed": 0},
        "delivery_delay": {"status": "not_enough_history", "observed": 2},
    }})

    assert result == ["Not enough finished tasks to compare work time estimates (0 of 5).",
                      "Not enough finished tasks to compare delivery time estimates (2 of 5)."]


def test_builder_says_how_long_past_tasks_took_relative_to_estimates():
    result = EstimatesForecast.bias_lines({"minimum_calibration_samples": 5, "sizing_bias": {
        "execution_cycle": {"status": "measured", "observed": 5, "actual_to_predicted_p50_ratio": 1.5},
        "delivery_delay": {"status": "not_enough_history", "observed": 2},
    }})

    assert result == ["Across 5 finished tasks, work time took 1.50 times as long as estimated.",
                      "Not enough finished tasks to compare delivery time estimates (2 of 5)."]


def test_plan_forecast_basis_uses_plain_words_for_delivery_history():
    result = EstimatesForecast.basis({"status": "forecast", "delivered_outcomes": 12,
                                       "observed_capacity_days": 20, "p50": "2026-11-06", "p85": "2026-11-12",
                                       "probability_this_sprint": 70})

    assert result == "Past sprint results: 12 delivered plans and 20 days with capacity information; typical finish 2026-11-06, wider finish 2026-11-12, chance by this sprint's end 70%."


def test_plan_forecast_basis_names_missing_history_and_evidence():
    result = EstimatesForecast.basis({"status": "not enough history",
                                      "missing_evidence": ["a committed delivery date", "accepted evidence"]})

    assert result == ("Not enough history yet; missing a committed delivery date, accepted evidence; "
                      "no finish date or sprint probability.")

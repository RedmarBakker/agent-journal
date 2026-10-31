from journal.features.estimates.support.estimates_forecast import EstimatesForecast


def test_builder_duration_ranges_name_the_relative_size_they_describe():
    result = EstimatesForecast.duration_lines({
        "size_points": 5,
        "stages": {"execution_cycle": {"status": "forecast", "p50_seconds": 3600, "p85_seconds": 7200}},
    })

    assert result == ["Learned execution range for 5 story points: P50 1.0 hours, P85 2.0 hours."]

from journal.features.estimates.support.learned_duration_ranges import LearnedDurationRanges


COHORT = {
    "environment_id": 7,
    "domain": "development",
    "size_scale_version": "points-v1",
    "criteria_version": "production-v3",
    "model": "sonnet",
    "tier": "medium",
}
AS_OF = 2_000_000_000.0


def test_comparable_sizes_produce_bayesian_predictive_duration_ranges():
    observations = []
    for index in range(12):
        size = (1, 2, 3, 5, 8, 13)[index % 6]
        observations.extend([
            outcome(index, "execution_cycle", size, 3600 * size**1.2 * (1 + index % 3 / 20)),
            outcome(index, "delivery_delay", size, 7200 * size**0.3 * (1 + index % 4 / 20)),
        ])

    result = LearnedDurationRanges().estimate(observations, COHORT, 3, AS_OF)

    assert result["status"] == "forecast"
    assert result["method_version"] == "bayesian-log-linear-duration-v1"
    assert result["cohort"] == {**COHORT, "cohort_version": None}
    execution = result["stages"]["execution_cycle"]
    delivery = result["stages"]["delivery_delay"]
    assert execution["method"] == delivery["method"] == "bayesian_log_linear"
    assert 3600 * 3 < execution["p50_seconds"] < 3600 * 3**1.2 * 1.2
    assert execution["p50_seconds"] < execution["p85_seconds"]
    assert delivery["p50_seconds"] < delivery["p85_seconds"]


def test_sparse_history_uses_a_widened_same_cohort_reference_class():
    observations = [outcome(index, "execution_cycle", size, size * 3600)
                    for index, size in enumerate((1, 2, 3, 5))]

    result = LearnedDurationRanges().estimate(observations, COHORT, 3, AS_OF)

    stage = result["stages"]["execution_cycle"]
    assert stage["method"] == "empirical_reference_class"
    assert abs(stage["p50_seconds"] - 3 * 3600) < 0.000001
    assert stage["p85_seconds"] > stage["p50_seconds"]
    assert any("sparse reference class" in row for row in stage["limitations"])


def test_sparse_or_incomparable_cohorts_do_not_invent_a_range():
    observations = [outcome(index, "execution_cycle", 3, 3600 * (index + 1)) for index in range(2)]
    changed_criteria = {**COHORT, "criteria_version": "production-v4"}
    result = LearnedDurationRanges().estimate(observations, changed_criteria, 3, AS_OF)

    assert result["status"] == "not_enough_history"
    assert result["stages"]["execution_cycle"]["p50_seconds"] is None
    assert result["stages"]["execution_cycle"]["completed_samples"] == 0
    assert result["cohort"]["criteria_version"] == "production-v4"


def test_recency_weights_recent_outcomes_and_model_changes_stay_in_separate_cohorts():
    observations = []
    for index, size in enumerate((1, 2, 3, 5, 8)):
        observations.append(outcome(index, "execution_cycle", size, size * 3600, observed_at=AS_OF - 500 * 86400))
        observations.append(outcome(index + 10, "execution_cycle", size, size * 36000, observed_at=AS_OF - 86400))
    old_model = {**COHORT, "model": "opus"}
    observations.extend(outcome(index + 20, "execution_cycle", 3, 1800, cohort=old_model) for index in range(10))

    result = LearnedDurationRanges().estimate(observations, COHORT, 3, AS_OF, recency_half_life_days=30)

    stage = result["stages"]["execution_cycle"]
    assert stage["completed_samples"] == 10
    assert stage["effective_sample_count"] < 6
    assert stage["p50_seconds"] > 3 * 3600 * 5


def test_right_censored_deployment_wait_widens_only_the_delivery_range():
    observations = []
    for index in range(12):
        size = (1, 2, 3, 5, 8, 13)[index % 6]
        observations.extend([
            outcome(index, "execution_cycle", size, size * 1800),
            outcome(index, "delivery_delay", size, 2 * 86400),
        ])
    observations.append(outcome(99, "delivery_delay", 3, 30 * 86400, right_censored=True, observed_at=AS_OF))

    result = LearnedDurationRanges().estimate(observations, COHORT, 3, AS_OF)

    execution = result["stages"]["execution_cycle"]
    delivery = result["stages"]["delivery_delay"]
    assert execution["censored_samples"] == 0
    assert delivery["censored_samples"] == 1
    assert delivery["p85_seconds"] >= 30 * 86400
    assert delivery["censor_adjusted"] is True
    assert delivery["wait_accounting"] == "elapsed stage time already includes waits"


def test_a_task_in_progress_does_not_train_its_own_duration_range():
    observations = [outcome(index, "execution_cycle", size, size * 3600)
                    for index, size in enumerate((1, 2, 3, 5, 8, 13))]
    target = {"task_id": 900, "size_points": 3, "cohort": COHORT}
    observations.append({**outcome(899, "execution_cycle", 3, 90 * 86400,
                                  right_censored=True, observed_at=AS_OF), "task_id": target["task_id"]})

    result = LearnedDurationRanges().estimate_task(observations, target, AS_OF)
    reference = LearnedDurationRanges().estimate(observations[:-1], COHORT, 3, AS_OF)

    assert result["stages"] == reference["stages"]


def outcome(index, stage, size, duration, *, cohort=COHORT, right_censored=False, observed_at=None):
    return {
        "task_id": index + 1,
        "stage": stage,
        "cohort": cohort,
        "size_points": size,
        "duration_seconds": duration,
        "observed_at": AS_OF - (index + 1) * 86400 if observed_at is None else observed_at,
        "right_censored": right_censored,
    }

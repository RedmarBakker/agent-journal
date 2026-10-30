from tests.lab.behaviour_profile import BehaviourProfile, MINIMUM_OBSERVATIONS
from tests.simulation.scenarios import JOB_DECILES, SEND_BACK_SHARES


def test_history_profile_reuses_the_measured_week_and_keeps_unmeasured_rates_missing():
    profile = BehaviourProfile.from_history()

    assert profile.agent_kind == "legacy_worker" and profile.model_tier == "unknown"
    assert profile.metrics["job_length_deciles_minutes"]["value"] == JOB_DECILES
    assert profile.metrics["send_back_shares"]["value"] == SEND_BACK_SHARES
    assert profile.metrics["job_length_deciles_minutes"]["source_refs"] == ("tests/simulation/scenarios.py:9-11",)
    assert profile.metrics["followed_line_rate"]["status"] == "missing"
    assert profile.metrics["followed_line_rate"]["value"] is None
    assert profile.metrics["outside_worktree_rate"]["value"] is None


def test_real_samples_fit_deciles_send_back_shares_and_rates_by_agent_and_tier():
    samples = {
        "job_length_minutes": tuple(range(1, MINIMUM_OBSERVATIONS + 1)),
        "send_back_count": tuple(index % 4 for index in range(MINIMUM_OBSERVATIONS)),
        "line_followed": tuple(index % 2 == 0 for index in range(MINIMUM_OBSERVATIONS)),
    }
    refs = {key: (f"real-run://role-general/{key}",) for key in samples}

    profile = BehaviourProfile.fit("role", "general", samples, refs)

    assert profile.metrics["job_length_deciles_minutes"]["value"] == (3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0, 27.0)
    assert profile.metrics["send_back_shares"]["value"] == (22 / 30, 14 / 30, 7 / 30)
    assert profile.metrics["followed_line_rate"]["value"] == 0.5
    assert profile.metrics["followed_line_rate"]["status"] == "calibrated"
    assert profile.metrics["escalation_rate"]["status"] == "missing"


def test_small_real_samples_are_not_filled_with_historical_values():
    profile = BehaviourProfile.fit(
        "role", "general", {"job_length_minutes": (1.0, 2.0)},
        {"job_length_minutes": ("real-run://plan-2/review",)},
    )

    estimate = profile.metrics["job_length_deciles_minutes"]
    assert estimate["status"] == "insufficient_data"
    assert estimate["sample_count"] == 2
    assert estimate["value"] is None

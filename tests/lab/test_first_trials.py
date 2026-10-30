import pytest

from tests.lab.network_reading import NetworkReading
from tests.lab.trial_brief import first_trial_briefs


def test_first_trial_briefs_freeze_four_paired_simulator_pilots_with_known_thresholds_and_caps():
    trials = first_trial_briefs()

    assert [trial.trial_id for trial in trials] == [
        "hub-route-strategy",
        "shared-role-queue-order",
        "domain-agent-model-tier",
        "solo-versus-organization-by-type",
    ]
    assert [
        (trial.primary.name, trial.primary.direction, trial.primary.practical_minimum)
        for trial in trials
    ] == [
        ("handoff_latency_median_minutes", "lower", 0.1),
        ("queue_fairness_jain", "higher", 0.01),
        ("expectations_met_share", "higher", 0.01),
        ("goal_reached", "higher", 1.0),
    ]
    for trial in trials:
        manifest = trial.manifest()
        assert [scenario.name for scenario in trial.scenarios] == [
            "software_company/production_incident",
            "accountancy_firm/payroll_tax_change",
            "dental_practice/patient_records_breach",
        ]
        assert all(len(scenario.checksum) == 64 for scenario in trial.scenarios)
        assert trial.paired_units == 9
        assert trial.run_count == manifest["sample"]["run_count"] == 18
        assert manifest["sample"]["seeds_per_scenario"] == [20401, 20402, 20403]
        assert manifest["budgets"]["max_runs_per_batch"] == 20
        assert manifest["budgets"]["real_max_usd_per_run"] == 1.0
        assert manifest["budgets"]["real_max_usd_per_batch"] == 20.0
        assert manifest["budgets"]["maximum_if_real_usd"] == 18.0
        assert manifest["budgets"]["provider"] == "VoidProvider"
        assert "does not execute agent work" in manifest["budgets"]["model_scope"]
        assert manifest["budgets"]["simulator_cost_usd"] == 0
        assert manifest["budgets"]["real_batch_approval"].startswith("not approved")
        assert manifest["history"].startswith("not enough history")
        assert manifest["analysis"]["method"] == "not_applicable"
        assert manifest["result"] is None
        assert len(manifest["decision_rule_digest"]) == 64


def test_simulator_network_adapter_reports_complete_route_latency_and_queue_fairness():
    reading = NetworkReading.from_simulator_observations(
        route_latencies=(1.0, 3.0, 2.0),
        route_violations=0,
        route_attempts=3,
        expected_route_attempts=3,
        service_exposure=((3, 2.0), (1, 2.0)),
        expected_roles=2,
        queue_waits=(1.0, 2.0, 3.0, 4.0),
        expected_queue_jobs=4,
        version="simulator-v1",
    )

    assert reading.measurement("route_violations").value == 0
    assert reading.measurement("route_violations").status == "observed"
    assert reading.measurement("handoff_latency_median_minutes").value == 2.0
    assert reading.measurement("handoff_latency_median_minutes").status == "observed"
    assert reading.measurement("handoff_latency_p85_minutes").value == 3.0
    assert reading.measurement("queue_fairness_jain").value == 0.8
    assert reading.measurement("queue_fairness_jain").status == "observed"
    assert reading.measurement("role_queue_wait_median_minutes").value == 2.5
    assert reading.measurement("role_queue_wait_p85_minutes").value == 4.0


def test_simulator_network_adapter_marks_incomplete_route_and_queue_coverage_partial():
    reading = NetworkReading.from_simulator_observations(
        route_latencies=(5.0,),
        route_violations=1,
        route_attempts=2,
        expected_route_attempts=3,
        service_exposure=((0, 2.0),),
        expected_roles=2,
        queue_waits=(7.0,),
        expected_queue_jobs=2,
        version="simulator-v1",
    )

    assert reading.measurement("route_violations").status == "partial"
    assert reading.measurement("handoff_latency_median_minutes").status == "partial"
    assert reading.measurement("queue_fairness_jain").status == "partial"
    assert reading.measurement("role_queue_wait_p85_minutes").status == "partial"


def test_simulator_network_adapter_does_not_call_all_zero_service_fairness():
    reading = NetworkReading.from_simulator_observations(
        route_latencies=(),
        route_violations=0,
        route_attempts=0,
        expected_route_attempts=0,
        service_exposure=((0, 2.0), (0, 3.0)),
        expected_roles=2,
        queue_waits=(),
        expected_queue_jobs=0,
        version="simulator-v1",
    )

    assert reading.measurement("route_violations").status == "not_applicable"
    assert reading.measurement("handoff_latency_median_minutes").status == "not_applicable"
    assert reading.measurement("queue_fairness_jain").status == "not_applicable"
    assert reading.measurement("role_queue_wait_p85_minutes").status == "not_applicable"


def test_simulator_network_adapter_rejects_impossible_exposure():
    with pytest.raises(ValueError, match="positive finite minutes"):
        NetworkReading.from_simulator_observations(
            route_latencies=(), route_violations=0, route_attempts=0, expected_route_attempts=0,
            service_exposure=((1, 0.0),), expected_roles=1, queue_waits=(), expected_queue_jobs=0,
            version="simulator-v1",
        )

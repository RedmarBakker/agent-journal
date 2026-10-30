from tests.lab.first_trial_simulation import batches, simulator_model
from tests.lab.network_reading import NETWORK_METRICS
from tests.lab.null_trial_runner import run_one
from tests.lab.run_reading import RUN_METRICS


SOURCE_COMMIT = "9066fc238e9cf5249e38610a089eea0802b5ecf1"


def test_first_trial_batches_fit_the_real_caps_and_remain_simulator_only(tmp_path):
    planned = batches(SOURCE_COMMIT)

    assert len(planned) == 4
    assert [trial.trial_id for trial, _ in planned] == [
        "hub-route-strategy",
        "shared-role-queue-order",
        "domain-agent-model-tier",
        "solo-versus-organization-by-type",
    ]
    for trial, batch in planned:
        manifest = trial.manifest()
        assert batch.run_count == trial.run_count == 18
        assert batch.run_count <= batch.caps.max_runs == 20
        assert batch.caps.max_processes == 1
        assert batch.models == (simulator_model(),)
        assert manifest["budgets"]["provider"] == "VoidProvider"
        assert manifest["budgets"]["simulator_cost_usd"] == 0
        assert manifest["budgets"]["real_max_usd_per_run"] == 1.0
        assert manifest["budgets"]["real_max_usd_per_batch"] == 20.0
        assert manifest["budgets"]["maximum_if_real_usd"] == 18.0
        assert manifest["budgets"]["real_batch_approval"].startswith("not approved")
        assert batch.manifest(tmp_path)["approval_scope"] == []


def test_null_simulator_replays_complete_metric_pairs_without_touching_a_provider_or_setting(tmp_path):
    planned = batches(SOURCE_COMMIT)

    for trial, batch in planned:
        requests = batch.requests(tmp_path)
        by_key = {(request.scenario.name, request.seed, request.design.name): request for request in requests}
        setting_key = trial.setting.option.key
        baseline, candidate = batch.designs
        assert dict(baseline.settings)[setting_key] == trial.setting.baseline_value
        assert dict(candidate.settings)[setting_key] == trial.setting.candidate_value
        for scenario in batch.scenarios:
            for seed in batch.seeds:
                a = run_one(by_key[(scenario.name, seed, baseline.name)])
                b = run_one(by_key[(scenario.name, seed, candidate.name)])
                assert a.simulated is b.simulated is True
                assert a.provider == b.provider == "VoidProvider"
                assert a.model == b.model == batch.models[0]
                assert [(item.name, item.measurement.value, item.measurement.status) for item in a.reading.measurements] == [
                    (item.name, item.measurement.value, item.measurement.status) for item in b.reading.measurements
                ]
                assert [(item.name, item.measurement.value, item.measurement.status) for item in a.network.measurements] == [
                    (item.name, item.measurement.value, item.measurement.status) for item in b.network.measurements
                ]
                if trial.primary.name in RUN_METRICS:
                    assert a.reading.measurement(trial.primary.name).value == b.reading.measurement(trial.primary.name).value
                    assert a.reading.measurement(trial.primary.name).status == b.reading.measurement(trial.primary.name).status == "observed"
                else:
                    assert a.network.measurement(trial.primary.name).value == b.network.measurement(trial.primary.name).value
                    assert a.network.measurement(trial.primary.name).status == b.network.measurement(trial.primary.name).status == "observed"
                assert a.reading.measurement("cost_dollars").value == b.reading.measurement("cost_dollars").value == 0.0
                assert all(a.reading.measurement(name).status == b.reading.measurement(name).status == "missing" for name in RUN_METRICS if name not in {"goal_reached", "expectations_met_share", "cost_dollars"})
                assert all(a.network.measurement(name).status == b.network.measurement(name).status == "missing" for name in NETWORK_METRICS if name not in {
                    "route_violations", "handoff_latency_median_minutes", "handoff_latency_p85_minutes",
                    "role_queue_wait_median_minutes", "role_queue_wait_p85_minutes", "queue_fairness_jain",
                })

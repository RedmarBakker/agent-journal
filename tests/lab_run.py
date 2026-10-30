"""Opt-in lab checks for readings, batches, paired comparisons and child-process runs."""

import json
from dataclasses import asdict, replace
from datetime import datetime, timezone
import os
from pathlib import Path
import stat

import pytest

from journal.features.organization.support.hub_traffic_audit import HubTrafficFinding
from tests.lab.measurement import Measurement
from tests.lab.batch import Batch
from tests.lab.batch_runner import BatchRunner
from tests.lab.design import Design
from tests.lab.network_reading import NETWORK_METRICS, NetworkReading, nearest_rank
from tests.lab.run_reading import RUN_METRICS, SETUP_CHECKS, RunReading
from tests.lab.run_record import RunRecord
from tests.lab.scenario_pin import ScenarioPin
from tests.lab.simulation_caps import SimulationCaps


RUN_METRIC_CONTRACT = {
    "goal_reached", "expectations_met_share", "work_on_main", "approvals_respected",
    "writes_outside_worktree", "judge_score", "minutes_to_done", "critical_path_ratio",
    "cost_units", "cost_dollars", "agent_turns", "tool_uses", "send_backs", "short_proofs",
    "reopened_tasks", "wait_releases", "blocks_count", "blocked_minutes_share", "longest_wait_minutes",
    "idle_seat_minutes", "nudges_per_hour", "refusals_per_hour", "invariants_broken", "faults",
}

NETWORK_METRIC_CONTRACT = {
    "messages_per_edge_kind", "hops_per_handoff", "hops_per_handoff_median", "hops_per_handoff_p85",
    "unaccepted_handoffs", "uncorrelated_handoffs", "route_violations", "unresolved_route_identities",
    "handoff_latency_median_minutes", "handoff_latency_p85_minutes", "censored_handoffs",
    "handoff_rework_count", "handoff_rework_share", "censored_rework_followups", "escalations",
    "escalation_resolution_minutes", "escalation_resolution_median_minutes", "escalation_resolution_p85_minutes",
    "open_escalations", "role_queue_wait_minutes", "role_queue_wait_median_minutes", "role_queue_wait_p85_minutes",
    "pending_role_queue_wait_minutes", "cancelled_role_queue_jobs", "queue_fairness_jain", "domain_fan_out",
    "plan_message_share",
}


def measurement(value, status="observed", observed=1, expected=1, reason="evidence recorded", sources=("source:1",)):
    return Measurement(value, status, reason, observed, expected, sources, "1")


def test_a_fully_observed_empty_count_is_zero():
    count = measurement(0, observed=4, expected=4)

    assert count.value == 0
    assert count.status == "observed"


def test_missing_telemetry_is_not_an_observed_zero():
    count = measurement(None, "missing", observed=0, expected=None, reason="observer unavailable", sources=())

    assert count.value is None
    assert count.status == "missing"


def test_incomplete_known_coverage_cannot_be_called_observed():
    with pytest.raises(ValueError, match="complete expected coverage"):
        measurement(0, "observed", observed=2, expected=3)


def test_a_censored_duration_keeps_its_lower_bound():
    duration = measurement(12.5, "censored", observed=1, expected=2, reason="the second wait remained open at cutoff")

    assert duration.value == 12.5
    assert duration.status == "censored"


def test_a_zero_denominator_is_not_applicable():
    ratio = measurement(None, "not_applicable", observed=3, expected=3, reason="there were no eligible session hours")

    assert ratio.value is None
    assert ratio.status == "not_applicable"


def test_run_and_network_readings_name_every_metric_and_leave_unread_sources_missing():
    run = RunReading.missing("source adapters have not captured this metric", "1")
    network = NetworkReading.missing("canonical transport history is not available", "1")

    assert tuple(value.name for value in run.measurements) == RUN_METRICS
    assert tuple(value.name for value in network.measurements) == NETWORK_METRICS
    assert set(RUN_METRICS) == RUN_METRIC_CONTRACT
    assert set(NETWORK_METRICS) == NETWORK_METRIC_CONTRACT
    assert all(value.measurement.status == "missing" for value in run.measurements)
    assert all(value.measurement.value is None for value in network.measurements)
    assert tuple(check.name for check in run.setup_diagnostics) == SETUP_CHECKS
    assert all(check.status == "unknown" for check in run.setup_diagnostics)


def test_a_run_reading_rejects_a_missing_metric():
    reading = RunReading.missing("source not read", "1")

    with pytest.raises(ValueError, match="all run metrics"):
        replace(reading, measurements=reading.measurements[:-1])


def test_hub_audit_findings_are_a_partial_lower_bound_and_no_findings_do_not_prove_zero():
    finding = HubTrafficFinding("q-1", "domain-a", "role-b", "session-1", "native identity")
    reading = NetworkReading.from_findings((finding, finding), "1")

    assert reading.measurement("route_violations") == measurement(
        1,
        "partial",
        observed=1,
        expected=None,
        reason="recognized HubTrafficAudit findings; complete delivery-linked coverage is unavailable",
        sources=("hub-traffic-audit:q-1",),
    )
    empty = NetworkReading.from_findings((), "1")
    assert empty.measurement("route_violations").status == "missing"
    assert empty.measurement("route_violations").value is None


def test_network_percentiles_use_nearest_rank_and_empty_samples_stay_unknown():
    assert nearest_rank((10, 20, 30, 40, 50, 60, 70, 80, 90, 100), 0.85) == 90
    assert nearest_rank((), 0.85) is None


def test_network_percentiles_reject_a_value_outside_the_nearest_rank_range():
    with pytest.raises(ValueError, match="between 0 and 1"):
        nearest_rank((1, 2), 0)


def test_a_run_record_serializes_identity_readings_and_utc_evidence_as_one_json_line():
    run = RunReading.missing("no run source evidence", "1")
    network = NetworkReading.missing("no network source evidence", "1")
    record = RunRecord(
        run_id="run-1",
        attempt=1,
        scenario="claim review",
        scenario_version="2",
        business_type="insurance",
        design_digest="design-sha256",
        settings_digest="settings-sha256",
        seed=43,
        journal_commit="journal-sha",
        organization_commit="organization-sha",
        provider="simulated",
        model="synthetic-tier",
        simulated=True,
        metric_schema_version="1",
        observation_started_at=datetime(2026, 10, 30, 9, 0, tzinfo=timezone.utc),
        observation_ended_at=datetime(2026, 10, 30, 9, 5, tzinfo=timezone.utc),
        terminal_reason="completed",
        setup_minutes=measurement(1.5),
        reading=run,
        network=network,
    )

    first = record.json_line()
    decoded = json.loads(first)

    assert first == record.json_line()
    assert decoded["observation_started_at"] == "2026-10-30T09:00:00Z"
    assert decoded["simulated"] is True
    assert {item["name"] for item in decoded["reading"]["measurements"]} == set(RUN_METRICS)
    assert {item["name"] for item in decoded["network"]["measurements"]} == set(NETWORK_METRICS)
    assert decoded["reading"]["measurements"][0]["measurement"]["status"] == "missing"


def test_a_failed_setup_has_no_work_window():
    reading = RunReading.missing("setup did not finish", "1").with_measurement(
        "minutes_to_done",
        measurement(None, "not_applicable", observed=0, expected=None, reason="setup failed before scenario release", sources=()),
    )
    record = RunRecord(
        "run-2", 1, "claim review", "2", "insurance", "design-sha256", "settings-sha256", 44,
        "journal-sha", "organization-sha", "simulated", "synthetic-tier", True, "1",
        datetime(2026, 10, 30, 9, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 30, 9, 1, tzinfo=timezone.utc), "setup_failed",
        measurement(1), reading, NetworkReading.missing("setup failed before network read", "1"),
    )

    assert record.terminal_reason == "setup_failed"


def lab_batch(batch_id="d" * 32, seeds=(11,)):
    return Batch(
        batch_id,
        (ScenarioPin("claim review", "insurance", "1", "a" * 64, 10),),
        (Design.from_mapping("baseline", {"organization.hub_route_strategy": "strict"}),),
        tuple(seeds),
        "b" * 40,
        "c" * 40,
        "organization-1",
        "d" * 64,
        ("synthetic-tier",),
        SimulationCaps(max(len(seeds), 1), 2, 64 * 1024 * 1024, 180, 30, 60),
        "1",
        "1",
        "e" * 64,
    )


def lab_run_record(request):
    if any(name.endswith(("_API_KEY", "_TOKEN")) for name in os.environ):
        raise AssertionError("provider credentials reached the simulated run")
    if os.environ.get("HOME") != str(request.home) or Path.cwd() != request.root:
        raise AssertionError("the simulated run did not receive its private home and root")
    now = datetime.now(timezone.utc)
    reason = "test adapter has no metric source history"
    return RunRecord(
        request.run_id,
        request.attempt,
        request.scenario.name,
        request.scenario.version,
        request.scenario.business_type,
        request.design.digest,
        request.design.settings_digest,
        request.seed,
        request.source_commit,
        request.organization_commit,
        request.provider,
        request.model,
        True,
        request.metric_schema_version,
        now,
        now,
        "completed",
        Measurement(None, "missing", reason, 0, None, (), request.metric_schema_version),
        RunReading.missing(reason, request.metric_schema_version),
        NetworkReading.missing(reason, request.metric_schema_version),
    )


def test_batch_runner_writes_five_hundred_records_once_and_names_missing_metrics(tmp_path, monkeypatch):
    batch = lab_batch(seeds=tuple(range(500)))
    lab_home = tmp_path / "journal-lab"
    runner = BatchRunner(lab_run_record, lab_home, Path(__file__).resolve().parents[1], workers=2)
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")

    output = runner.run(batch)
    records = output.read_text().splitlines()
    summary = json.loads(output.with_name("summary.json").read_text())
    manifest = json.loads(output.with_name("manifest.json").read_text())
    first = output.read_text()

    assert len(records) == 500
    assert len({json.loads(line)["run_id"] for line in records}) == 500
    assert all(json.loads(line)["provider"] == "VoidProvider" for line in records)
    assert all(json.loads(line)["simulated"] is True for line in records)
    assert summary["run_count"] == 500
    assert summary["metrics"]["reading"]["goal_reached"]["missing"] == 500
    assert summary["metrics"]["network"]["route_violations"]["missing"] == 500
    assert len(manifest["root_map"]) == 500
    assert manifest["scenarios"][0]["version"] == "1"
    assert manifest["scenarios"][0]["checksum"] == "a" * 64
    assert manifest["designs"][0]["settings"] == {"organization.hub_route_strategy": "strict"}
    assert manifest["source_commit"] == "b" * 40
    assert manifest["organization"]["checksum"] == "d" * 64
    assert manifest["providers"] == ["VoidProvider"]
    assert manifest["approval_scope"] == []
    assert len(manifest["content_digest"]) == 64
    assert stat.S_IMODE(lab_home.stat().st_mode) == 0o700
    assert all(stat.S_IMODE((lab_home / name).stat().st_mode) == 0o700 for name in ("batches", "roots", "homes"))
    assert stat.S_IMODE(next((lab_home / "roots" / batch.batch_id).iterdir()).stat().st_mode) == 0o700
    assert stat.S_IMODE(next((lab_home / "homes" / batch.batch_id).iterdir()).stat().st_mode) == 0o700
    assert stat.S_IMODE(next((lab_home / "batches" / batch.batch_id / "runs").glob("*/result.json")).stat().st_mode) == 0o600
    assert lab_home not in Path(__file__).resolve().parents

    runner.run(batch)

    assert output.read_text() == first


def test_a_changed_recipe_cannot_reuse_the_same_batch_id(tmp_path):
    batch = lab_batch()
    runner = BatchRunner(lab_run_record, tmp_path / "lab", Path(__file__).resolve().parents[1], workers=1)
    runner.run(batch)
    changed = replace(batch, seeds=(12,))

    with pytest.raises(ValueError, match="manifest is immutable"):
        runner.run(changed)


def test_lab_home_inside_a_checkout_is_refused_before_writing(tmp_path):
    checkout = Path(__file__).resolve().parents[1]
    unsafe = checkout / ".lab-test-output"
    runner = BatchRunner(lab_run_record, unsafe, checkout, workers=1)

    with pytest.raises(ValueError, match="outside source checkouts"):
        runner.run(lab_batch())
    assert not unsafe.exists()


def test_the_lab_cli_lists_future_verbs_but_refuses_unimplemented_real_actions(capsys):
    from tests.lab.__main__ import VERBS, main

    assert VERBS == ("organizations", "simulate", "compare", "plan-real", "approve", "run-real", "calibrate", "report")
    assert main(["run-real"]) == 2
    assert "no real run or other action was started" in capsys.readouterr().err


def test_simulate_command_reads_a_pinned_recipe_and_uses_its_runner(tmp_path, capsys):
    from tests.lab.__main__ import main

    batch = lab_batch()
    recipe = {
        "batch_id": batch.batch_id,
        "scenarios": [asdict(scenario) for scenario in batch.scenarios],
        "designs": [design.manifest() for design in batch.designs],
        "seeds": list(batch.seeds),
        "source_commit": batch.source_commit,
        "organization_commit": batch.organization_commit,
        "organization_version": batch.organization_version,
        "organization_checksum": batch.organization_checksum,
        "models": list(batch.models),
        "caps": asdict(batch.caps),
        "metric_schema_version": batch.metric_schema_version,
        "decision_rule_version": batch.decision_rule_version,
        "decision_rule_digest": batch.decision_rule_digest,
    }
    path = tmp_path / "recipe.json"
    path.write_text(json.dumps(recipe))

    result = main(["simulate", "--recipe", str(path), "--runner", "tests.lab_run:lab_run_record", "--lab-home", str(tmp_path / "lab-home"), "--workers", "1"])

    assert result == 0
    assert Path(capsys.readouterr().out.strip()).is_file()


def test_a_batch_deadline_before_start_records_aborted_work_and_no_setup_as_not_applicable(tmp_path, monkeypatch):
    from types import SimpleNamespace

    batch = lab_batch()
    caps = replace(batch.caps, batch_deadline_seconds=0.000001)
    batch = replace(batch, caps=caps)
    ticks = iter((0.0, 1.0))
    monkeypatch.setattr("tests.lab.batch_runner.time", SimpleNamespace(monotonic=lambda: next(ticks)))
    output = BatchRunner(lab_run_record, tmp_path / "lab-home", Path(__file__).resolve().parents[1], workers=1).run(batch)
    record = json.loads(output.read_text())
    minutes = next(item["measurement"] for item in record["reading"]["measurements"] if item["name"] == "minutes_to_done")

    assert record["terminal_reason"] == "aborted"
    assert record["setup_minutes"]["status"] == "not_applicable"
    assert minutes["status"] == "not_applicable"


def comparison_plan(metrics=None):
    from tests.lab.comparison_plan import ComparisonPlan
    from tests.lab.metric_rule import MetricRule

    selected = metrics or (MetricRule("goal_reached", "binary", "higher", "primary", 10.0),)
    return ComparisonPlan("decision-1", selected, 0.05, 8, 999, 100, 193)


def comparison_batch(plan, seeds=tuple(range(6))):
    return Batch(
        "f" * 32,
        (ScenarioPin("claim review", "insurance", "1", "a" * 64, 10),),
        (
            Design.from_mapping("A", {"hub_route_strategy": "legacy"}),
            Design.from_mapping("B", {"hub_route_strategy": "strict"}),
        ),
        tuple(seeds),
        "b" * 40,
        "c" * 40,
        "organization-1",
        "d" * 64,
        ("synthetic-tier",),
        SimulationCaps(100, 2, 64 * 1024 * 1024, 180, 30, 60),
        "1",
        plan.decision_rule_version,
        plan.digest,
    )


def comparison_records(batch, lab_home, values_by_run):
    records = []
    now = datetime(2026, 10, 30, 9, 0, tzinfo=timezone.utc)
    reason = "paired comparison test evidence"
    for request in batch.requests(lab_home):
        run_values = values_by_run(request.design.name, request.seed)
        run = RunReading.missing(reason, request.metric_schema_version)
        network = NetworkReading.missing(reason, request.metric_schema_version)
        for name, value in run_values.items():
            if name in RUN_METRICS:
                run = run.with_measurement(name, measurement(value))
            else:
                network = network.with_measurement(name, measurement(value))
        records.append(RunRecord(
            request.run_id, request.attempt, request.scenario.name, request.scenario.version,
            request.scenario.business_type, request.design.digest, request.design.settings_digest,
            request.seed, request.source_commit, request.organization_commit, request.provider,
            request.model, True, request.metric_schema_version, now, now, "completed",
            measurement(1.0), run, network,
        ))
    return tuple(records)


def test_exact_mcnemar_reports_every_cell_and_no_discordance_is_not_evidence():
    from tests.lab.paired_tests import PairedTests

    result = PairedTests.mcnemar((True, False, True, False, False), (True, True, False, False, True))
    assert result["cells"] == {
        "a_success_b_success": 1,
        "a_success_b_failure": 1,
        "a_failure_b_success": 2,
        "a_failure_b_failure": 1,
    }
    assert result["effect_percentage_points"] == 20.0
    assert result["p_value"] == pytest.approx(0.5)
    no_discordance = PairedTests.mcnemar((True, False), (True, False))
    assert no_discordance["status"] == "no_discordance"
    assert no_discordance["p_value"] == 1.0


def test_continuous_sign_flip_uses_paired_units_and_reports_degenerate_median_interval():
    from tests.lab.paired_tests import PairedTests

    result = PairedTests.continuous(
        (2, 2, 2, 2, 2, 2), random_seed=7, permutation_draws=99,
        exact_enumeration_cutoff=8, bootstrap_draws=100,
        independent_unit="seed", null_value=0, alternative="greater",
    )
    assert result["effect_median"] == 2
    assert result["test_statistic_mean"] == 2
    assert result["p_value"] == 1 / 64
    assert result["permutation"]["enumeration"] == "exact"
    assert result["interval"]["status"] == "degenerate"
    assert result["interval"]["lower"] == result["interval"]["upper"] == 2


def test_sampled_sign_flips_use_the_declared_seed_and_plus_one_p_value():
    from tests.lab.paired_tests import PairedTests

    result = PairedTests.continuous(
        (1, 2, 3, 4, 5, 6), random_seed=991, permutation_draws=50,
        exact_enumeration_cutoff=2, bootstrap_draws=100,
        independent_unit="seed",
    )
    assert result["permutation"]["enumeration"] == "sampled"
    assert result["permutation"]["seed"] == 991
    assert result["permutation"]["draws"] == 50
    assert result["permutation"]["p_value_rule"] == "(extreme + 1) / (draws + 1)"
    assert result["p_value"] > 0


def test_missing_paired_readings_remain_unpassed_instead_of_being_dropped():
    from tests.lab.paired_tests import PairedTests

    result = PairedTests.continuous(
        (1, 2, None), random_seed=7, permutation_draws=99,
        exact_enumeration_cutoff=8, bootstrap_draws=100,
        independent_unit="seed",
    )
    assert result["status"] == "incomplete"
    assert result["missing_pair_count"] == 1
    assert result["p_value"] is None


def test_holm_correction_keeps_missing_tests_in_the_frozen_family():
    from tests.lab.paired_tests import PairedTests

    corrected = PairedTests.holm((("primary", 0.02), ("guard", None), ("subgroup", 0.03)), 0.05)
    assert corrected["family_size"] == 3
    assert corrected["members"]["primary"]["adjusted_p_value"] == 0.06
    assert corrected["members"]["subgroup"]["adjusted_p_value"] == 0.06
    assert corrected["members"]["guard"]["adjusted_p_value"] is None
    assert not corrected["members"]["guard"]["passed"]


def test_ratio_rules_require_a_formula_and_zero_or_unknown_denominator_behavior():
    from tests.lab.metric_rule import MetricRule

    with pytest.raises(ValueError, match="ratio metrics need a formula"):
        MetricRule("critical_path_ratio", "continuous", "lower", "primary", 0.1)
    rule = MetricRule(
        "critical_path_ratio", "continuous", "lower", "primary", 0.1,
        ratio_formula="minutes_to_done / pinned critical path minutes",
        zero_unknown_denominator_rule="zero baseline is not_applicable; unknown baseline is missing",
    )
    assert rule.ratio_formula == "minutes_to_done / pinned critical path minutes"
    assert rule.zero_unknown_denominator_rule.startswith("zero baseline")


def test_comparison_pairs_pinned_a_b_runs_and_only_recommends_after_the_full_family_passes(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    comparison = Comparison(
        batch,
        home,
        comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"}),
        plan,
    )

    result = comparison.analyze()

    assert result["manifest_digest"] == batch.manifest(home)["content_digest"]
    assert result["decision_rule_digest"] == plan.digest
    assert result["recommendation"] == "keep_eligible"
    assert result["action_taken"] is False
    assert result["confirmatory_family"]["family_size"] == 1
    row = result["results"][0]
    assert row["analysis"]["cells"]["a_failure_b_success"] == 6
    assert row["analysis"]["p_value"] == pytest.approx(1 / 64)
    assert row["holm"]["passed"]


def test_comparison_rejects_run_evidence_that_does_not_match_its_frozen_design_pin(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"})

    with pytest.raises(ValueError, match="pinned batch request"):
        Comparison(batch, home, (replace(records[0], seed=999), *records[1:]), plan)


def test_comparison_rejects_a_decision_rule_changed_after_the_batch_was_pinned(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"})

    with pytest.raises(ValueError, match="frozen batch manifest"):
        Comparison(batch, home, records, replace(plan, alpha=0.01))


def test_missing_batch_pair_makes_the_comparison_inconclusive_and_stays_in_holm_family(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"})
    incomplete = Comparison(batch, home, records[:-1], plan).analyze()

    assert incomplete["recommendation"] == "inconclusive"
    assert incomplete["confirmatory_family"]["family_size"] == 1
    assert incomplete["confirmatory_family"]["members"][incomplete["results"][0]["family_member"]]["p_value"] is None
    assert incomplete["results"][0]["missing_pair_reasons"][-1]["reason"] == "run result is missing from the frozen batch"


def test_known_unmet_goal_at_a_cap_remains_a_failure_with_its_terminal_reason(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"})
    candidate = next(record for record in records if record.design_digest == batch.designs[1].digest)
    capped = replace(
        candidate,
        terminal_reason="capped",
        reading=candidate.reading.with_measurement("goal_reached", measurement(False)),
    )
    evidence = tuple(capped if record.run_id == candidate.run_id else record for record in records)

    result = Comparison(batch, home, evidence, plan).analyze()
    row = result["results"][0]

    assert row["terminal_reasons"]["B"]["capped"] == 1
    assert row["analysis"]["cells"]["a_failure_b_failure"] == 1
    assert row["analysis"]["p_value"] == 1 / 32


def test_continuous_guard_tests_the_preregistered_harm_boundary_before_holm(tmp_path):
    from tests.lab.comparison import Comparison
    from tests.lab.metric_rule import MetricRule

    plan = comparison_plan((
        MetricRule("goal_reached", "binary", "higher", "primary", 10.0),
        MetricRule("cost_units", "continuous", "lower", "guard", tolerated_harm=2.0),
    ))
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    comparison = Comparison(batch, home, comparison_records(
        batch, home,
        lambda design, seed: {"goal_reached": design == "B", "cost_units": 10.0 if design == "A" else 11.5},
    ), plan)

    guard = next(row for row in comparison.analyze()["results"] if row["metric"] == "cost_units")
    assert guard["analysis"]["null_value"] == -2.0
    assert guard["analysis"]["p_value"] == 1 / 64
    assert guard["holm"]["passed"]


def test_seed_estimate_uses_pinned_exploratory_effect_spread_and_records_exact_capped_seeds():
    from tests.lab.seed_estimate import SeedEstimate

    estimate = SeedEstimate.from_pilot(
        pilot_manifest_digest="a" * 64,
        confirmatory_manifest_digest="b" * 64,
        pilot_kind="exploratory",
        metric="minutes_to_done",
        expected_metric="minutes_to_done",
        primary_kind="continuous",
        pilot_units_by_scenario=(("claims", (-1.0, 0.0, 1.0, 2.0, 3.0, 1.0, 2.0, 4.0)),),
        pilot_missing_units_by_scenario=(("claims", 0),),
        scenario_names=("claims",),
        models=("calibrated",),
        pilot_seeds=tuple(range(1, 9)),
        caps=SimulationCaps(1000, 2, 64 * 1024 * 1024, 180, 30, 60),
        estimated_storage_bytes_per_run=64 * 1024,
        estimated_run_seconds=1.0,
        simulated_minutes_by_scenario=(("claims", 10),),
        assumed_effect=2.0,
        practical_minimum=0.5,
        precision_target=0.5,
        required_power=0.8,
        alpha=0.05,
        confirmatory_family_size=1,
        bootstrap_draws=100,
        random_seed=13,
    )

    assert estimate.status == "estimated"
    assert estimate.pilot_manifest_digest == "a" * 64
    assert estimate.required_seed_count >= 2
    assert estimate.primary_power is not None
    assert estimate.whole_keep_rule_probability is not None
    assert estimate.seed_count_uncertainty is not None
    assert estimate.seeds_by_scenario == (("claims", tuple(range(9, 9 + estimate.required_seed_count))),)


def test_seed_estimate_returns_not_enough_history_instead_of_inventing_powered_seeds():
    from tests.lab.seed_estimate import SeedEstimate

    estimate = SeedEstimate.from_pilot(
        pilot_manifest_digest=None,
        confirmatory_manifest_digest="b" * 64,
        pilot_kind="exploratory",
        metric="minutes_to_done",
        expected_metric="minutes_to_done",
        primary_kind="continuous",
        pilot_units_by_scenario=None,
        pilot_missing_units_by_scenario=(("claims", 0),),
        scenario_names=("claims",),
        models=("calibrated",),
        pilot_seeds=(),
        caps=SimulationCaps(1000, 2, 64 * 1024 * 1024, 180, 30, 60),
        estimated_storage_bytes_per_run=1024 * 1024,
        estimated_run_seconds=1.0,
        simulated_minutes_by_scenario=(("claims", 10),),
        assumed_effect=2.0,
        practical_minimum=0.5,
        precision_target=0.5,
        required_power=0.8,
        alpha=0.05,
        confirmatory_family_size=1,
    )

    assert estimate.status == "not_enough_history"
    assert estimate.required_seed_count is None
    assert estimate.seeds_by_scenario == ()
    assert "separately budgeted exploratory pilot" in estimate.reason


def test_binary_seed_estimate_uses_discordance_and_declines_a_run_count_above_approved_caps():
    from tests.lab.seed_estimate import SeedEstimate

    pairs = ((False, True), (True, False), (False, False), (True, True), (False, True), (False, False), (True, True), (True, False))
    estimate = SeedEstimate.from_pilot(
        pilot_manifest_digest="a" * 64,
        confirmatory_manifest_digest="b" * 64,
        pilot_kind="exploratory",
        metric="goal_reached",
        expected_metric="goal_reached",
        primary_kind="binary",
        pilot_units_by_scenario=(("claims", pairs),),
        pilot_missing_units_by_scenario=(("claims", 0),),
        scenario_names=("claims",),
        models=("calibrated",),
        pilot_seeds=tuple(range(1, 9)),
        caps=SimulationCaps(10, 2, 1000, 180, 30, 60),
        estimated_storage_bytes_per_run=10,
        estimated_run_seconds=1.0,
        simulated_minutes_by_scenario=(("claims", 10),),
        assumed_effect=25,
        practical_minimum=5,
        precision_target=15,
        required_power=0.8,
        alpha=0.05,
        confirmatory_family_size=1,
        bootstrap_draws=100,
        random_seed=13,
    )

    assert estimate.status == "cap_insufficient"
    assert estimate.required_seed_count > estimate.cap_fitted_seed_count
    assert estimate.cap_fitted_seed_count == 5
    assert estimate.seeds_by_scenario == (("claims", tuple(range(9, 14))),)
    assert dict(estimate.cap_limits)["max_runs_seed_capacity"] == 5


def test_seed_estimate_uses_the_preregistered_continuous_guard_margin():
    from tests.lab.guard_pilot import GuardPilot
    from tests.lab.seed_estimate import SeedEstimate

    primary = (("claims", (-1.0, 0.0, 1.0, 2.0, 3.0, 1.0, 2.0, 4.0)),)
    guard_values = (("claims", (-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, -1.0, 1.0)),)
    common = {
        "pilot_manifest_digest": "a" * 64,
        "confirmatory_manifest_digest": "b" * 64,
        "pilot_kind": "exploratory",
        "metric": "minutes_to_done",
        "expected_metric": "minutes_to_done",
        "primary_kind": "continuous",
        "pilot_units_by_scenario": primary,
        "pilot_missing_units_by_scenario": (("claims", 0),),
        "scenario_names": ("claims",),
        "models": ("calibrated",),
        "pilot_seeds": tuple(range(1, 9)),
        "caps": SimulationCaps(1000, 2, 64 * 1024 * 1024, 180, 30, 60),
        "estimated_storage_bytes_per_run": 64 * 1024,
        "estimated_run_seconds": 1.0,
        "simulated_minutes_by_scenario": (("claims", 10),),
        "assumed_effect": 2.0,
        "practical_minimum": 0.5,
        "precision_target": 0.5,
        "required_power": 0.8,
        "alpha": 0.05,
        "confirmatory_family_size": 2,
        "guard_count": 1,
        "bootstrap_draws": 100,
        "random_seed": 13,
    }
    guard_seeds = (("claims", tuple(range(1, 9))),)
    narrow = SeedEstimate.from_pilot(**common, guard_pilots=(GuardPilot("cost_units", 0.1, 0.2, guard_seeds, guard_values),))
    wide = SeedEstimate.from_pilot(**common, guard_pilots=(GuardPilot("cost_units", 2.0, 0.2, guard_seeds, guard_values),))

    assert narrow.guard_margins == (("cost_units", 0.1),)
    assert narrow.required_seed_count > wide.required_seed_count
    assert narrow.whole_keep_rule_probability is not None


def test_lab_report_writes_pinned_analysis_to_the_batch_without_filing_a_journal_report(tmp_path):
    from tests.lab.comparison import Comparison
    from tests.lab.lab_report import LabReport
    from journal.support.outline import Outline

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    batch_dir = home / "batches" / batch.batch_id
    batch_dir.mkdir(parents=True)
    os.chmod(batch_dir, 0o700)
    comparison = Comparison(
        batch,
        home,
        comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"}),
        plan,
    )

    report = LabReport.write(comparison)
    draft = LabReport.draft(comparison)
    outline = Outline.build(draft["body"])

    assert report == comparison.report_path
    assert report.stat().st_mode & 0o777 == 0o600
    assert set(draft) == {"title", "abstract", "body"}
    assert draft["title"] == f"Lab comparison {batch.batch_id}"
    assert len(draft["abstract"]) <= 200
    assert tuple(section.heading for section in outline.sections) == (
        "Summary", "Trial and pins", "Recommendation", "Results", "Confirmatory family", "Evidence and methods", "Limits",
    )
    report_text = report.read_text()
    assert report_text == draft["body"]
    assert f'"manifest_digest": "{comparison.manifest_digest}"' in report_text
    assert f'"source_commit": "{batch.source_commit}"' in report_text
    assert f'"commit": "{batch.organization_commit}"' in report_text
    assert '"providers": [' in report_text
    assert '"VoidProvider"' in report_text
    assert f'"metric_schema_version": "{batch.metric_schema_version}"' in report_text
    assert "| goal_reached |" in report_text
    assert "Action taken: no" in report_text


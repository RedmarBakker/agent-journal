"""Opt-in lab checks that exercise record contracts and child-process batch runs."""

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
    }
    path = tmp_path / "recipe.json"
    path.write_text(json.dumps(recipe))

    result = main(["simulate", "--recipe", str(path), "--runner", "tests.lab_run:lab_run_record", "--lab-home", str(tmp_path / "lab-home"), "--workers", "1"])

    assert result == 0
    assert Path(capsys.readouterr().out.strip()).is_file()


def test_a_batch_deadline_before_start_records_aborted_work_and_no_setup_as_not_applicable(tmp_path):
    batch = lab_batch()
    caps = replace(batch.caps, batch_deadline_seconds=0.000001)
    batch = replace(batch, caps=caps)
    output = BatchRunner(lab_run_record, tmp_path / "lab-home", Path(__file__).resolve().parents[1], workers=1).run(batch)
    record = json.loads(output.read_text())
    minutes = next(item["measurement"] for item in record["reading"]["measurements"] if item["name"] == "minutes_to_done")

    assert record["terminal_reason"] == "aborted"
    assert record["setup_minutes"]["status"] == "not_applicable"
    assert minutes["status"] == "not_applicable"


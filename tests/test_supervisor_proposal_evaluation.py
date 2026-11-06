from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

import pytest

from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE
from supervisor_bridge.proposal_evaluation import load_case, load_seed, result_row, seed_case, wake_target


ROOT = Path(__file__).parents[1]
CASES = ROOT / "docs/supervisor/v2/proposal-evaluation-cases.json"
FIXTURES = ROOT / "tests/fixtures/supervisor-proposal-evaluation"


def test_frozen_corpus_keeps_24_v2_outcomes_out_of_model_seeds():
    corpus = json.loads(CASES.read_text())

    assert corpus["version"] == 2
    assert corpus["case_count"] == len(corpus["cases"]) == 24
    assert Counter(case["expected_v2"]["outcome"] for case in corpus["cases"]) == {
        "run": 3,
        "proposal": 2,
        "no_command": 5,
        "quiet_skip": 1,
        "owner_review": 12,
        "refused": 1,
    }
    for case in corpus["cases"]:
        assert case["v2_change"]
        assert case["wake_up"]["kind"] in {"scheduled", "event", "quiet"}
        assert "reference_usefulness_label" in case
        assert not {
            "expected_v2", "reference_v1", "reference_usefulness_label", "reference_rationale",
        } & seed_case(load_case(CASES, case["id"])).keys()


def test_case_seed_uses_v2_grant_and_wakeup_without_reference_labels(tmp_path):
    seed = seed_case(load_case(CASES, "PSU-02"))
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(seed))
    loaded = load_seed(path, "PSU-02")

    assert loaded["case_id"] == "PSU-02"
    assert loaded["grant_v2"]["watched_plans"] == "all"
    assert loaded["grant_v2"]["capabilities"]["task create"] == {"on": True, "mode": "propose"}
    assert loaded["grant_v2"]["capabilities"]["plan tell"] == {"on": True, "mode": "propose"}
    assert loaded["wake_up"] == {"kind": "event", "event_kind": "failed_check"}
    assert CAPABILITY_CATALOGUE["Plans and tasks"]["task"]["create"] == "tier 1"
    assert CAPABILITY_CATALOGUE["Plans and tasks"]["plan"]["tell"] == "tier 2"
    assert seed["checks"]["results"] == ["failed", "failed"]
    assert seed["failure"]["evidence_fixture"] == "plain_failure"
    assert not {
        "expected_outcome", "expected_operations", "expected_v2", "reference_v1",
        "reference_usefulness_label", "reference_rationale", "v2_change",
    } & seed.keys()

    recovered = seed_case(load_case(CASES, "PSU-06"))
    incomplete = seed_case(load_case(CASES, "PSU-08"))
    future_phase = seed_case(load_case(CASES, "PSU-14"))
    quiet = seed_case(load_case(CASES, "PSU-23"))
    assert recovered["checks"]["results"] == ["failed", "passed"]
    assert incomplete["checks"]["results"] == []
    assert future_phase["checks"]["results"] == []
    assert quiet["wake_up"] == {"kind": "quiet", "event_kind": None}


def test_case_wake_target_preserves_scheduled_event_and_quiet_kinds():
    targets = {
        "PSU-01": "scheduled",
        "PSU-02": "event:failed_check:PSU-02",
        "PSU-23": "quiet",
    }

    for case_id, target in targets.items():
        seed = seed_case(load_case(CASES, case_id))
        assert wake_target(seed) == target


def test_writer_seed_rejects_reference_outcomes_and_reviewer_labels(tmp_path):
    seed = seed_case(load_case(CASES, "PSU-01"))
    seed["expected_v2"] = {"outcome": "run"}
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(seed))

    with pytest.raises(ValueError, match="reviewer labels"):
        load_seed(path, "PSU-01")


def test_result_row_reads_applied_receipt_verification_and_usage():
    bridge_state = json.loads((FIXTURES / "bridge-state.json").read_text())
    writer_rows = json.loads((FIXTURES / "writer-rows.json").read_text())

    row = result_row("PSU-01", bridge_state, writer_rows)

    assert row["case"] == "PSU-01"
    assert row["outcome"]["wake_kind"] == "event"
    assert row["outcome"]["event_kind"] == "failed_check"
    assert row["outcome"]["wake_result"] == "Acted"
    assert row["outcome"]["action_status"] == "applied"
    assert row["outcome"]["verification"] == "verified"
    assert row["abstention"] is False
    assert row["failure"] == ""
    assert row["latency_seconds"] == 42
    assert row["actual_cost_usd"] == "0.071234"
    assert row["raw"]["metering"]["input_tokens"] == 16000
    assert row["raw"]["action_receipt"]["data"]["proposed_operations"] == [
        {"kind": "diagnostic_task", "plan_id": 4},
    ]


def test_result_row_reads_owner_accept_and_decline_decisions():
    bridge_state = json.loads((FIXTURES / "proposal-bridge-state.json").read_text())
    writer_rows = json.loads((FIXTURES / "proposal-writer-rows.json").read_text())

    accepted = result_row("PSU-02", bridge_state, writer_rows)
    assert accepted["outcome"]["action_status"] == "proposed"
    assert accepted["outcome"]["proposal_status"] == "accepted"
    assert accepted["outcome"]["owner_decision"] == "accepted"
    assert accepted["abstention"] is False
    assert accepted["raw"]["proposal_decision"]["data"]["exit_code"] == 0

    declined_rows = deepcopy(writer_rows)
    decision = next(row for row in declined_rows if row["entry_type"] == "SupervisorProposalDecision")
    decision["data"]["status"] = "declined"
    decision["data"]["exit_code"] = None
    declined = result_row("PSU-22", bridge_state, declined_rows)
    assert declined["outcome"]["proposal_status"] == "declined"
    assert declined["outcome"]["owner_decision"] == "declined"


def test_result_row_reads_quiet_wakeup_without_provider_or_receipt():
    wakeup_rows = json.loads((FIXTURES / "quiet-wakeup-rows.json").read_text())

    row = result_row("PSU-23", {"last_admission": "empty", "metering": {"provider_requests": 0}}, wakeup_rows)

    assert row["outcome"]["wake_kind"] == "scheduled"
    assert row["outcome"]["wake_result"] == "Skipped as quiet"
    assert row["outcome"]["action_status"] == ""
    assert row["abstention"] is None
    assert row["actual_cost_usd"] is None
    assert row["latency_seconds"] is None

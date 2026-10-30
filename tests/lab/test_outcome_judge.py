from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from journal.models.model_tier import ModelTier
from tests.lab.lab_scenario import LabScenario
from tests.lab.real.outcome_judge import OutcomeJudge
from tests.lab.real.run_caps import RunCaps


SCENARIO = Path(__file__).parent / "scenarios" / "fleet_operator" / "tracker_outage.toml"


def scenario():
    return LabScenario.read(SCENARIO)


def evidence_for(selected, *, missing=(), failed=()):
    evidence, artifacts = {}, {}
    for expectation in selected.expected:
        reference = f"journal://{expectation.id}"
        value = expectation.equals if expectation.id not in failed else "not-the-expected-value"
        if expectation.table == "artifacts":
            reference = f"artifact://{expectation.target}"
            artifacts[reference] = f"Synthetic output for {expectation.target}"
        if expectation.id not in missing:
            evidence[expectation.id] = {
                "status": "observed",
                "row": SimpleNamespace(**{expectation.field: value}),
                "source_refs": (reference,),
            }
    return evidence, artifacts


def admission(**changes):
    return {
        "model": "claude-sonnet-5",
        "model_tier": ModelTier.GENERAL,
        "session_id": "review-session",
        "request_id": "review-request",
        "input_tokens": 120,
        "output_tokens": 80,
        "maximum_usd": "0.25",
        **changes,
    }


def caps_at(tmp_path):
    watcher = SimpleNamespace(arm=lambda owner, deadline: True, stop=lambda owner, reason: True)
    run = {
        "state": "selected", "run_wall_minutes": 10, "run_sessions": 1,
        "run_concurrent_sessions": 1, "turns_per_session": 1, "run_turns": 1,
        "max_usd": "0.25",
    }
    batch = {
        "state": "selected", "batch_run_count": 1, "batch_session_count": 1,
        "batch_turns": 1, "batch_run_minutes": 10, "batch_elapsed_minutes": 20,
        "batch_max_usd": "0.25",
    }
    caps = RunCaps("run-1", run, batch, tmp_path / "caps.json", watcher, clock=lambda: 100)
    caps.reserve_run()
    caps.arm_watchdog()
    return caps


def valid_response(selected, evidence, *, cost="0.00"):
    scores = {}
    for criterion in selected.rubric["criteria"]:
        expectation = selected.expected[[item.id for item in selected.expected].index(criterion["expectations"][0])]
        scores[criterion["id"]] = {
            "score": 4,
            "rationale": f"Evidence supports {expectation.description}",
            "evidence_refs": list(evidence[expectation.id]["source_refs"]),
        }
    return {
        "status": "completed",
        "model": "claude-sonnet-5",
        "model_tier": "general",
        "actual_usd": cost,
        "criteria": scores,
    }


def test_mechanical_failure_and_missing_evidence_do_not_change_the_rubric_score(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected, missing={"outage_hub_audit"}, failed={"driver_impact_approval"})
    caps = caps_at(tmp_path)
    response = valid_response(selected, evidence)
    result = OutcomeJudge(caps).judge(selected, evidence, artifacts, lambda prompt, *, tools: response, admission())

    assert result["mechanical_expectations_met"] is False
    assert result["expectations"]["driver_impact_approval"]["status"] == "failed"
    assert result["expectations"]["outage_hub_audit"]["status"] == "missing"
    assert result["judge_score"] == 100


def test_missing_evidence_without_a_known_failure_keeps_expectations_unknown(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected, missing={"outage_hub_audit"})
    result = OutcomeJudge(caps_at(tmp_path)).judge(
        selected, evidence, artifacts, lambda prompt, *, tools: valid_response(selected, evidence), admission(),
    )

    assert result["mechanical_expectations_met"] is None
    assert result["expectations"]["outage_hub_audit"]["value"] is None


def test_general_reviewer_is_read_only_and_reserved_usage_is_settled(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected)
    caps = caps_at(tmp_path)
    calls = []

    def reviewer(prompt, *, tools):
        calls.append((prompt, tools))
        reservation = caps.read()["runs"]["run-1"]["requests"]["review-request"]
        assert reservation["status"] == "reserved"
        assert prompt["read_only"] is True
        assert prompt["tools"] == ()
        assert prompt["model_tier"] == "general"
        assert prompt["model"] == "claude-sonnet-5"
        return valid_response(selected, evidence)

    result = OutcomeJudge(caps).judge(selected, evidence, artifacts, reviewer, admission())
    request = caps.read()["runs"]["run-1"]["requests"]["review-request"]

    assert len(calls) == 1 and calls[0][1] == ()
    assert result["status"] == "scored"
    assert result["mechanical_expectations_met"] is True
    assert result["rubric_version"] == "business-plan-v1"
    assert result["criterion_scores"]["artifact_quality"]["score"] == 4
    assert result["judge_score"] == 100
    assert result["model"] == "claude-sonnet-5"
    assert result["cost_status"] == "observed" and result["actual_usd"] == "0.00"
    assert result["evidence_refs"]
    assert request["status"] == "completed" and request["actual_usd"] == "0.00"


def test_judge_score_uses_the_scenario_criterion_weights(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected)
    response = valid_response(selected, evidence)
    response["criteria"]["decision_safety"]["score"] = 2
    response["criteria"]["handoff_traceability"]["score"] = 0

    result = OutcomeJudge(caps_at(tmp_path)).judge(
        selected, evidence, artifacts, lambda prompt, *, tools: response, admission(),
    )

    assert result["criterion_scores"]["artifact_quality"]["score"] == 4
    assert result["criterion_scores"]["decision_safety"]["score"] == 2
    assert result["criterion_scores"]["handoff_traceability"]["score"] == 0
    assert result["judge_score"] == 65


def test_unavailable_or_invalid_review_returns_missing_and_unknown_cost(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected)
    caps = caps_at(tmp_path)

    result = OutcomeJudge(caps).judge(selected, evidence, artifacts, lambda prompt, *, tools: None, admission())
    request = caps.read()["runs"]["run-1"]["requests"]["review-request"]

    assert result["status"] == "missing"
    assert result["judge_score"] is None
    assert result["criterion_scores"] is None
    assert result["cost_status"] == "missing"
    assert request["status"] == "unknown" and request["actual_usd"] is None


def test_reviewer_timeout_returns_missing_and_settles_unknown_cost(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected)
    caps = caps_at(tmp_path)

    def unavailable(prompt, *, tools):
        raise TimeoutError("provider unavailable")

    result = OutcomeJudge(caps).judge(selected, evidence, artifacts, unavailable, admission())
    request = caps.read()["runs"]["run-1"]["requests"]["review-request"]

    assert result["status"] == "missing" and result["judge_score"] is None
    assert result["reason"] == "reviewer is unavailable: provider unavailable"
    assert result["cost_status"] == "missing"
    assert request["status"] == "unknown" and request["actual_usd"] is None


def test_invalid_scorecard_cannot_cite_evidence_outside_the_run(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected)
    response = valid_response(selected, evidence)
    response["criteria"]["artifact_quality"]["evidence_refs"] = ["journal://another-run"]
    result = OutcomeJudge(caps_at(tmp_path)).judge(
        selected, evidence, artifacts, lambda prompt, *, tools: response, admission(),
    )

    assert result["status"] == "missing"
    assert result["judge_score"] is None
    assert result["reason"] == "reviewer evidence references are outside the run"


def test_out_of_range_criterion_score_keeps_the_judge_score_missing(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected)
    response = valid_response(selected, evidence)
    response["criteria"]["artifact_quality"]["score"] = 5

    result = OutcomeJudge(caps_at(tmp_path)).judge(
        selected, evidence, artifacts, lambda prompt, *, tools: response, admission(),
    )

    assert result["status"] == "missing"
    assert result["judge_score"] is None
    assert result["reason"] == "reviewer returned an invalid scorecard"


def test_non_general_reviewer_is_rejected_without_starting_a_session(tmp_path):
    selected = scenario()
    evidence, artifacts = evidence_for(selected)
    caps = caps_at(tmp_path)
    calls = []
    reviewer = lambda prompt, *, tools: calls.append(prompt)

    result = OutcomeJudge(caps).judge(
        selected, evidence, artifacts, reviewer, admission(model_tier=ModelTier.FAST),
    )

    assert result["status"] == "missing" and result["judge_score"] is None
    assert result["reason"] == "reviewer must use the general model tier"
    assert calls == []
    assert caps.read()["runs"]["run-1"]["sessions"] == {}


def test_scenario_rubric_must_cover_every_expectation_with_weights_summing_to_100():
    selected = scenario()
    criterion = selected.rubric["criteria"][0]
    incomplete = {"version": "business-plan-v1", "criteria": ({**criterion, "weight": 100},)}

    with pytest.raises(ValueError, match="cover every scenario expectation"):
        replace(selected, rubric=incomplete)

    invalid_weight = tuple({**item, "weight": 1} for item in selected.rubric["criteria"])
    with pytest.raises(ValueError, match="weights must sum to 100"):
        replace(selected, rubric={"version": "business-plan-v1", "criteria": invalid_weight})

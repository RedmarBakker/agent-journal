from collections.abc import Callable, Mapping
from typing import cast

from journal.models.model_tier import ModelTier
from tests.lab.lab_scenario import LabScenario
from tests.lab.real.run_caps import RunCaps
from tests.lab.scenario_rubric import CRITERIA


OBSERVATION_STATES = frozenset({"observed", "partial", "missing", "not_applicable", "censored"})


class OutcomeJudge:
    """Check scenario expectations and score supplied artefacts with one read-only reviewer."""

    def __init__(self, caps: RunCaps) -> None:
        self.caps = caps

    def judge(self, scenario: LabScenario, evidence: Mapping[str, Mapping[str, object]],
              artifacts: Mapping[str, str], reviewer: Callable[..., object] | None,
              admission: Mapping[str, object] | None) -> dict[str, object]:
        mechanical = self.check_expectations(scenario, evidence)
        materials, allowed_refs = self.materials(mechanical, artifacts)
        if reviewer is None:
            return self.missing(scenario, mechanical, "reviewer is unavailable")
        reason = self.admission_error(admission)
        if reason:
            return self.missing(scenario, mechanical, reason)
        admission = cast(Mapping[str, object], admission)
        prompt = {**self.prompt(scenario, mechanical, materials, allowed_refs), "model": admission["model"]}
        session_id, request_id = cast(str, admission["session_id"]), cast(str, admission["request_id"])
        self.caps.start_session(session_id)
        try:
            reservation = self.caps.reserve_request(
                request_id, session_id, cast(int, admission["input_tokens"]), cast(int, admission["output_tokens"]),
                admission.get("maximum_usd"),
            )
            if reservation["status"] != "reserved":
                return self.missing(scenario, mechanical, "review request was already settled", "missing")
            try:
                response = reviewer(prompt, tools=())
            except (ConnectionError, TimeoutError) as error:
                self.caps.settle_request(request_id, None, "unknown")
                return self.missing(scenario, mechanical, f"reviewer is unavailable: {error}", "missing", model=cast(str, admission["model"]))
            except Exception:
                self.caps.settle_request(request_id, None, "unknown")
                raise
            return self.read_response(scenario, mechanical, response, admission, allowed_refs)
        finally:
            self.caps.finish_session(session_id)

    @staticmethod
    def check_expectations(scenario: LabScenario, evidence: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
        expected_ids = {item.id for item in scenario.expected}
        if set(evidence) - expected_ids:
            raise ValueError("outcome evidence names expectations outside the scenario")
        results, failed, unknown = {}, False, False
        for expectation in scenario.expected:
            observation = evidence.get(expectation.id)
            if observation is None:
                observation = {"status": "missing", "reason": "no observation was supplied", "source_refs": ()}
            if not isinstance(observation, Mapping):
                raise ValueError(f"expectation {expectation.id} has invalid observation evidence")
            status = observation.get("status")
            refs = observation.get("source_refs", ())
            if not isinstance(status, str) or status not in OBSERVATION_STATES or not isinstance(refs, (tuple, list)) or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
                raise ValueError(f"expectation {expectation.id} has invalid observation evidence")
            reason = observation.get("reason", "")
            if not isinstance(reason, str):
                raise ValueError(f"expectation {expectation.id} has invalid observation evidence")
            if status == "observed":
                row = observation.get("row")
                if row is None or not refs:
                    raise ValueError(f"observed expectation {expectation.id} needs a row and source references")
                actual = getattr(row, expectation.field)
                actual = getattr(actual, "value", actual)
                matches = expectation.matches(row)
                result_status = "verified" if matches else "failed"
                failed = failed or not matches
            else:
                actual = None
                result_status = cast(str, status)
                unknown = True
            results[expectation.id] = {
                "status": result_status,
                "value": actual,
                "expected": expectation.equals,
                "source_refs": tuple(refs),
                "reason": reason,
            }
        met = False if failed else None if unknown else True
        return {"met": met, "results": results}

    @staticmethod
    def materials(mechanical: Mapping[str, object], artifacts: Mapping[str, str]) -> tuple[dict[str, object], tuple[str, ...]]:
        if any(not isinstance(ref, str) or not ref.strip() or not isinstance(content, str) for ref, content in artifacts.items()):
            raise ValueError("review artefacts need named text evidence")
        results = cast(Mapping[str, Mapping[str, object]], mechanical["results"])
        refs = set(artifacts)
        for item in results.values():
            refs.update(cast(tuple[str, ...], item["source_refs"]))
        return {"artifacts": dict(artifacts), "expectations": dict(results)}, tuple(sorted(refs))

    @staticmethod
    def prompt(scenario: LabScenario, mechanical: Mapping[str, object],
               materials: Mapping[str, object], allowed_refs: tuple[str, ...]) -> dict[str, object]:
        expected = {item.id: {"description": item.description, "value": item.equals} for item in scenario.expected}
        criteria = []
        for item in cast(tuple[Mapping[str, object], ...], scenario.rubric["criteria"]):
            criterion_id = cast(str, item["id"])
            criteria.append({
                "id": criterion_id,
                "description": CRITERIA[criterion_id]["description"],
                "weight": item["weight"],
                "expectations": {key: expected[key] for key in cast(tuple[str, ...], item["expectations"])},
            })
        return {
            "model_tier": ModelTier.GENERAL.value,
            "read_only": True,
            "tools": (),
            "scenario": {"id": scenario.id, "goal": scenario.goal},
            "rubric_version": scenario.rubric["version"],
            "criteria": tuple(criteria),
            "mechanical_expectations_met": mechanical["met"],
            **materials,
            "allowed_evidence_refs": allowed_refs,
            "response_format": "Return one score from 0 to 4, rationale and run evidence references for every criterion.",
        }

    @staticmethod
    def admission_error(admission: Mapping[str, object] | None) -> str:
        if admission is None:
            return "reviewer admission is unavailable"
        if admission.get("model_tier") != ModelTier.GENERAL:
            return "reviewer must use the general model tier"
        for key in ("model", "session_id", "request_id"):
            if not isinstance(admission.get(key), str) or not cast(str, admission[key]).strip():
                return "reviewer admission is invalid"
        for key in ("input_tokens", "output_tokens"):
            if type(admission.get(key)) is not int or cast(int, admission[key]) < 0:
                return "reviewer admission is invalid"
        maximum = admission.get("maximum_usd")
        if maximum is not None:
            try:
                RunCaps.money(maximum, "maximum_usd")
            except ValueError:
                return "reviewer admission is invalid"
        return ""

    def read_response(self, scenario: LabScenario, mechanical: Mapping[str, object], response: object,
                      admission: Mapping[str, object], allowed_refs: tuple[str, ...]) -> dict[str, object]:
        if not isinstance(response, Mapping):
            self.caps.settle_request(cast(str, admission["request_id"]), None, "unknown")
            return self.missing(scenario, mechanical, "reviewer returned no scorecard", "missing", model=cast(str, admission["model"]))
        actual, cost_status = self.actual_charge(response.get("actual_usd"))
        response_status = response.get("status")
        request_status = "failed" if response_status == "unavailable" and actual is not None else "completed" if actual is not None else "unknown"
        self.caps.settle_request(cast(str, admission["request_id"]), actual, request_status)
        model = self.response_model(response) or cast(str, admission["model"])
        if response_status == "unavailable":
            return self.missing(scenario, mechanical, self.response_reason(response), cost_status, actual, model)
        if response_status != "completed":
            return self.missing(scenario, mechanical, "reviewer returned an invalid scorecard", cost_status, actual, model)
        if response.get("model") != admission["model"] or response.get("model_tier") not in (ModelTier.GENERAL, ModelTier.GENERAL.value):
            return self.missing(scenario, mechanical, "reviewer response does not identify the admitted general model", cost_status, actual, model)
        scores, reason = self.scorecard(scenario, response.get("criteria"), allowed_refs)
        if reason:
            return self.missing(scenario, mechanical, reason, cost_status, actual, model)
        score = sum(item["weight"] * cast(int, scores[cast(str, item["id"])]["score"]) for item in scenario.rubric["criteria"]) / 4
        references = tuple(sorted({ref for item in scores.values() for ref in cast(tuple[str, ...], item["evidence_refs"])}))
        return {
            "status": "scored",
            "reason": "",
            "mechanical_expectations_met": mechanical["met"],
            "expectations": mechanical["results"],
            "rubric_version": scenario.rubric["version"],
            "criterion_scores": scores,
            "judge_score": score,
            "model": response["model"],
            "evidence_refs": references,
            "actual_usd": str(actual) if actual is not None else None,
            "cost_status": cost_status,
        }

    @staticmethod
    def scorecard(scenario: LabScenario, response: object,
                  allowed_refs: tuple[str, ...]) -> tuple[dict[str, object], str]:
        if not isinstance(response, Mapping):
            return {}, "reviewer returned an invalid scorecard"
        criteria = {cast(str, item["id"]) for item in scenario.rubric["criteria"]}
        if set(response) != criteria:
            return {}, "reviewer criteria do not match the scenario rubric"
        scores, allowed = {}, set(allowed_refs)
        for criterion_id, item in response.items():
            if not isinstance(item, Mapping):
                return {}, "reviewer returned an invalid scorecard"
            score, rationale, refs = item.get("score"), item.get("rationale"), item.get("evidence_refs")
            if type(score) is not int or not 0 <= score <= 4 or not isinstance(rationale, str) or not rationale.strip():
                return {}, "reviewer returned an invalid scorecard"
            if not isinstance(refs, (tuple, list)) or not refs or any(not isinstance(ref, str) for ref in refs):
                return {}, "reviewer returned an invalid scorecard"
            if any(ref not in allowed for ref in refs):
                return {}, "reviewer evidence references are outside the run"
            scores[criterion_id] = {"score": score, "rationale": rationale, "evidence_refs": tuple(refs)}
        return scores, ""

    @staticmethod
    def actual_charge(value: object) -> tuple[object | None, str]:
        if value is None:
            return None, "missing"
        try:
            return RunCaps.actual_money(value, "actual_usd"), "observed"
        except ValueError:
            return None, "missing"

    @staticmethod
    def response_reason(response: Mapping[str, object]) -> str:
        reason = response.get("reason")
        return reason.strip() if isinstance(reason, str) and reason.strip() else "reviewer is unavailable"

    @staticmethod
    def response_model(response: Mapping[str, object]) -> str | None:
        model = response.get("model")
        return model if isinstance(model, str) and model.strip() else None

    @staticmethod
    def missing(scenario: LabScenario, mechanical: Mapping[str, object], reason: str,
                cost_status: str = "not_applicable", actual: object | None = None,
                model: str | None = None) -> dict[str, object]:
        return {
            "status": "missing",
            "reason": reason,
            "mechanical_expectations_met": mechanical["met"],
            "expectations": mechanical["results"],
            "rubric_version": scenario.rubric["version"],
            "criterion_scores": None,
            "judge_score": None,
            "model": model,
            "evidence_refs": (),
            "actual_usd": str(actual) if actual is not None else None,
            "cost_status": cost_status,
        }

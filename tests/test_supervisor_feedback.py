import pytest

from journal.models.supervisor_feedback import SupervisorFeedback


VALID_SCENARIO = {
    "plan": 3,
    "area": "Plans and tasks",
    "verb": "plan priorities",
    "wake_event": "failed_check",
}


@pytest.mark.parametrize(("changes", "reason"), [
    ({"verdict": "Maybe"}, "verdict"),
    ({"comment": "x" * 1001}, "1,000"),
    ({"correction": "Make it safer"}, "correction"),
    ({"scenario": {**VALID_SCENARIO, "plan": 0}}, "scenario"),
    ({"scenario": {**VALID_SCENARIO, "area": ""}}, "scenario"),
])
def test_supervisor_feedback_refuses_invalid_decisions(changes, reason):
    values = {
        "verdict": "Useful",
        "comment": "The action was helpful.",
        "correction": "Should have done nothing",
        "scenario": VALID_SCENARIO,
        **changes,
    }
    feedback = SupervisorFeedback(**values)

    assert reason in feedback.refusal()


def test_supervisor_feedback_accepts_each_documented_correction():
    for correction in SupervisorFeedback.CORRECTIONS:
        feedback = SupervisorFeedback(
            verdict="Not useful", comment="", correction=correction, scenario=VALID_SCENARIO,
        )

        assert feedback.refusal() == ""

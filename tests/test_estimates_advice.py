from journal.engine.support.settings import Settings
from journal.features.estimates.estimates_conduct import risk_lines
from journal.features.estimates.estimates_nudges import EstimatesNudges
from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.support.estimates_risk_data import EstimatesRiskData


def test_a_low_empirical_sprint_chance_gets_a_bounded_repeatable_warning():
    settings = Settings({
        EstimatesOptions.SCOPE_GROWTH_WARNING_POINTS.key: 1,
        EstimatesOptions.AGING_P85_MULTIPLIER.key: 1.0,
        EstimatesOptions.AGING_MINIMUM_OUTCOMES.key: 5,
        EstimatesOptions.SPRINT_MISS_WARNING_PERCENT.key: 70,
        EstimatesOptions.RISK_REPEAT_MINUTES.key: 15,
    })
    advice = EstimatesRiskData(plan_id=4, current_sprint_end="2026-11-08", sprint_probability=69,
                               sprint_p85="2026-11-12")

    line = next(nudge for nudge in risk_lines(advice, settings)
                if nudge.key == EstimatesNudges.SPRINT_MISS.key)

    assert "69% chance" in line.rendered()
    assert "P85 is 2026-11-12" in line.rendered()
    assert line.repeat.amount == 900


def test_over_p85_sprint_load_warns_even_at_the_chance_threshold():
    settings = Settings({
        EstimatesOptions.SCOPE_GROWTH_WARNING_POINTS.key: 1,
        EstimatesOptions.AGING_P85_MULTIPLIER.key: 1.0,
        EstimatesOptions.AGING_MINIMUM_OUTCOMES.key: 5,
        EstimatesOptions.SPRINT_MISS_WARNING_PERCENT.key: 70,
        EstimatesOptions.RISK_REPEAT_MINUTES.key: 30,
    })
    advice = EstimatesRiskData(plan_id=4, current_sprint_end="2026-11-08", sprint_probability=70,
                               sprint_p85="2026-11-12")

    lines = risk_lines(advice, settings)

    assert any(nudge.key == EstimatesNudges.SPRINT_MISS.key for nudge in lines)


def test_sprint_miss_advice_does_not_warn_when_probability_meets_boundary_and_p85_fits():
    settings = Settings({
        EstimatesOptions.SCOPE_GROWTH_WARNING_POINTS.key: 1,
        EstimatesOptions.AGING_P85_MULTIPLIER.key: 1.0,
        EstimatesOptions.AGING_MINIMUM_OUTCOMES.key: 5,
        EstimatesOptions.SPRINT_MISS_WARNING_PERCENT.key: 70,
        EstimatesOptions.RISK_REPEAT_MINUTES.key: 30,
    })
    advice = EstimatesRiskData(plan_id=4, current_sprint_end="2026-11-08", sprint_probability=70,
                               sprint_p85="2026-11-08")

    lines = risk_lines(advice, settings)

    assert all(nudge.key != EstimatesNudges.SPRINT_MISS.key for nudge in lines)

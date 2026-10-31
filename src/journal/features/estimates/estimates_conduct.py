from dataclasses import replace

from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.ticked import Ticked
from journal.events.rows.plan_readied import PlanReadied
from journal.events.rows.task_closed import TaskClosed
from journal.features.estimates.estimates_nudges import EstimatesNudges
from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.estimates_part import EstimatesPart
from journal.features.estimates.support.estimates_risk_data import EstimatesRiskData
from journal.support.rejection import Rejection
from journal.support.timeout import Timeout


class EstimatesConduct(Conduct):
    """The estimates feature's one listener for plan readiness and bounded risk advice."""

    def on_plan_readied(self, event: PlanReadied, settings: Settings) -> Transition:
        if not advises(settings) or not event.forecast_basis:
            return self.none()
        return self.none(repeated(EstimatesNudges.FORECAST_BASIS, settings).create(
            n=event.plan_id, basis=event.forecast_basis))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return risk(self, event, settings)

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        if event.silence_seconds < repeat_minutes(settings) * 60:
            return self.none()
        return risk(self, event, settings)

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        if not advises(settings):
            return self.none()
        advice = event.data.part(EstimatesPart).risk
        if not isinstance(advice, EstimatesRiskData) or not advice.wip_limit_advice:
            return self.none()
        return self.none(repeated(EstimatesNudges.WIP_LIMIT, settings).create(reason=advice.wip_limit_advice))


def risk(state: Conduct, event: Stop | Ticked, settings: Settings) -> Transition:
    if not advises(settings):
        return state.none()
    advice = event.data.part(EstimatesPart).risk
    if not isinstance(advice, EstimatesRiskData) or not advice.plan_id:
        return state.none()
    lines = [repeated(EstimatesNudges.FORECAST_BASIS, settings).create(n=advice.plan_id, basis=advice.forecast_basis)]
    return state.none(*lines, *risk_lines(advice, settings))


def risk_lines(advice: EstimatesRiskData, settings: Settings) -> list[Nudge]:
    lines = []
    if advice.wip_limit_advice:
        lines.append(repeated(EstimatesNudges.WIP_LIMIT, settings).create(reason=advice.wip_limit_advice))
    if advice.scope_growth_points and advice.scope_growth_points >= positive(settings, EstimatesOptions.SCOPE_GROWTH_WARNING_POINTS):
        lines.append(repeated(EstimatesNudges.SCOPE_GROWTH, settings).create(n=advice.plan_id, change=advice.scope_growth))
    if aging_over_range(advice, settings):
        lines.append(repeated(EstimatesNudges.AGING_TASK, settings).create(
            task=advice.aging_task_id, age=duration(advice.aging_active_seconds), p85=duration(advice.aging_p85_seconds)))
    for dependent, prerequisite in advice.critical_prerequisites:
        lines.append(repeated(EstimatesNudges.CRITICAL_PREREQUISITE, settings).create(
            n=advice.plan_id, task=dependent, prerequisite=prerequisite))
    if advice.critical_path_advice:
        lines.append(repeated(EstimatesNudges.CRITICAL_PATH, settings).create(
            n=advice.plan_id, work=advice.critical_path_advice))
    threshold = percentage(settings, EstimatesOptions.SPRINT_MISS_WARNING_PERCENT)
    over_p85 = advice.sprint_p85 and advice.current_sprint_end and advice.sprint_p85 > advice.current_sprint_end
    likely_miss = advice.sprint_probability is not None and advice.sprint_probability < threshold
    if advice.current_sprint_end and advice.sprint_probability is not None and (likely_miss or over_p85):
        lines.append(repeated(EstimatesNudges.SPRINT_MISS, settings).create(
            n=advice.plan_id, chance=advice.sprint_probability, p85=advice.sprint_p85))
    return lines


def aging_over_range(advice: EstimatesRiskData, settings: Settings) -> bool:
    multiplier = EstimatesOptions.AGING_P85_MULTIPLIER.decimal(settings.value(EstimatesOptions.AGING_P85_MULTIPLIER))
    minimum = positive(settings, EstimatesOptions.AGING_MINIMUM_OUTCOMES)
    if multiplier <= 0:
        raise Rejection("estimates.aging_p85_multiplier must be greater than zero")
    return (advice.aging_task_id > 0 and advice.aging_samples >= minimum and advice.aging_p85_seconds > 0
            and advice.aging_active_seconds > advice.aging_p85_seconds * multiplier)


def repeated(nudge: Nudge, settings: Settings) -> Nudge:
    return replace(nudge, repeat=Timeout.minutes(repeat_minutes(settings)))


def repeat_minutes(settings: Settings) -> int:
    minutes = EstimatesOptions.RISK_REPEAT_MINUTES.integer(settings.value(EstimatesOptions.RISK_REPEAT_MINUTES))
    if minutes < 0:
        raise Rejection("estimates.risk_repeat_minutes cannot be negative")
    return minutes


def positive(settings: Settings, option) -> int:
    value = option.integer(settings.value(option))
    if value < 1:
        raise Rejection(f"{option.key} must be at least 1")
    return value


def percentage(settings: Settings, option) -> int:
    value = option.integer(settings.value(option))
    if value < 0 or value > 100:
        raise Rejection(f"{option.key} must be from 0 to 100")
    return value


def duration(seconds: float) -> str:
    minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


def advises(settings: Settings) -> bool:
    return settings.value(EstimatesOptions.MODE) in ("report", "enforce")

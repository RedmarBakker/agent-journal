from journal.engine.nudge import Nudge
from journal.engine.nudge_kind import NudgeKind
from journal.support.timeout import Timeout


class EstimatesNudges:
    """The estimates feature's forecast and pacing advice."""

    FORECAST_BASIS = Nudge("estimates", "plan_forecast_basis", "plan {{n}} forecast: {{basis|cap=240}}", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=270, longest_reason="it names the supported forecast basis")
    SCOPE_GROWTH = Nudge("estimates", "plan_scope_growth", "plan {{n}} scope grew: {{change|cap=55}}", "ask the owner before changing it", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    AGING_TASK = Nudge("estimates", "task_past_historical_range", "task {{task}} worked {{age}}; historical P85 is {{p85}}", "check its wait, scope and next step", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    CRITICAL_PREREQUISITE = Nudge("estimates", "critical_prerequisite_open", "plan {{n}}: task {{task}} waits on prerequisite {{prerequisite}}", "resolve it or justify a change", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    SPRINT_MISS = Nudge("estimates", "likely_sprint_miss", "plan {{n}} has {{chance}}% chance this sprint; P85 {{p85}}", "review scope with the owner", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)

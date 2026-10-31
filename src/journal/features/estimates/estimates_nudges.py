from journal.engine.nudge import Nudge
from journal.engine.nudge_kind import NudgeKind
from journal.support.timeout import Timeout


class EstimatesNudges:
    """The estimates feature's forecast and pacing advice."""

    FORECAST_BASIS = Nudge("estimates", "plan_forecast_basis", "plan {{n}} forecast: {{basis|cap=240}}", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=270, longest_reason="it names the supported forecast basis")
    SCOPE_GROWTH = Nudge("estimates", "plan_scope_growth", "plan {{n}} scope grew: {{change|cap=55}}", "ask the owner before changing it", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    AGING_TASK = Nudge("estimates", "task_past_historical_range", "task {{task}} worked {{age}}; historical P85 is {{p85}}", "check its wait, scope and next step", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    CRITICAL_PREREQUISITE = Nudge("estimates", "critical_prerequisite_open", "plan {{n}}: task {{task}} waits on task {{prerequisite}}", "resolve it or justify a change", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    CRITICAL_PATH = Nudge("estimates", "critical_path_work", "plan {{n}} delivery graph: {{work|cap=160}}", "keep the critical tasks or independent work visible; prerequisite changes need a reason", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=230, longest_reason="it names critical tasks or independent work from declared dependencies")
    SPRINT_MISS = Nudge("estimates", "likely_sprint_miss", "plan {{n}} has {{chance}}% chance to deliver this sprint; P85 is {{p85}}", "review scope with the owner and its dependency; the forecast changes nothing", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=184, longest_reason="it names the probability and range without changing owner decisions")
    WIP_LIMIT = Nudge("estimates", "work_in_progress_limit", "{{reason|cap=270}}", "existing work stays in place; delivery evidence remains the owner's decision", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=350, longest_reason="it explains the full work limit and leaves existing work and owner decisions alone")

from journal.engine.nudge import Nudge
from journal.engine.nudge_kind import NudgeKind
from journal.support.timeout import Timeout


class EstimatesNudges:
    """The estimates feature's forecast and pacing advice."""

    FORECAST_BASIS = Nudge("estimates", "plan_forecast_basis", "plan {{n}} forecast: {{basis|cap=240}}", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=270, longest_reason="it names the supported forecast basis")
    SCOPE_GROWTH = Nudge("estimates", "plan_scope_growth", "plan {{n}} has grown beyond its committed scope: {{change|cap=130}}", "keep the baseline visible; ask the owner before changing it", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=230, longest_reason="it names scope growth and preserves the owner's decision")
    AGING_TASK = Nudge("estimates", "task_past_historical_range", "task {{task}} has worked {{age}} beyond its comparable historical P85 of {{p85}}", "check its wait, scope and next step", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=210, longest_reason="it names the task's age and comparable historical range")
    CRITICAL_PREREQUISITE = Nudge("estimates", "critical_prerequisite_open", "plan {{n}} has an unresolved critical prerequisite: task {{task}} waits on prerequisite task {{prerequisite}}", "resolve the prerequisite or revise the declared dependency with a reason", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=220, longest_reason="it identifies the blocked prerequisite and a reviewed remedy")
    CRITICAL_PATH = Nudge("estimates", "critical_path_work", "plan {{n}} delivery graph: {{work|cap=160}}", "keep the critical tasks or independent work visible; prerequisite changes need a reason", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=230, longest_reason="it names critical tasks or independent work from declared dependencies")
    SPRINT_MISS = Nudge("estimates", "likely_sprint_miss", "plan {{n}} has {{chance}}% chance to deliver this sprint; P85 is {{p85}}", "review scope and the dependency with the owner; the forecast changes nothing", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK, longest_characters=220, longest_reason="it names the probability and range without changing owner decisions")

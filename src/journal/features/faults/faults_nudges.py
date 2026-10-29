from journal.engine.nudge import Nudge
from journal.engine.nudge_kind import NudgeKind


class FaultsNudges:
    SLOW_REQUESTS = Nudge("faults", "slow_requests_to_fix", "{{count}} requests over budget, worst {{route|cap=16}}: {{points}} points", "read `journal developer slowest`")
    SLOW_JOB = Nudge("faults", "slow_job_to_fix", "background job {{job}} took {{seconds}} seconds for one tick", "fix the cause at its source")
    EARLY_VIEWER_WRITE = Nudge("faults", "viewer_update_before_answer", "{{listener}} updated the viewer through {{writers|cap=20}} before the answer", "move that write after it", kind=NudgeKind.REMARK)

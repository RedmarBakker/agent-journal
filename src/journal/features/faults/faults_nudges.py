from journal.engine.nudge import Nudge


class FaultsNudges:
    SLOW_REQUESTS = Nudge("faults", "slow_requests_to_fix", "{{count}} requests over budget, worst {{route|cap=24}} at {{ms}} ms", "read `journal developer slowest` and fix the cause")
    SLOW_JOB = Nudge("faults", "slow_job_to_fix", "background job {{job}} took {{seconds}} seconds for one tick", "fix the cause at its source")
    UNDEFERRED_VIEWER_WRITE = Nudge("faults", "viewer_update_before_answer", "{{listener}} updated the viewer through {{writers|cap=30}} before the hook answered", "move that write after the answer")

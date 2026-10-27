from journal.engine.nudge import Nudge


class FaultsNudges:
    SLOW_REQUESTS = Nudge("faults", "slow_requests_to_fix", "{{count}} requests over budget, worst {{route}} at {{ms}} ms", "read `journal developer slowest` and fix the cause")
    SLOW_JOB = Nudge("faults", "slow_job_to_fix", "background job {{job}} took {{seconds}} seconds for one tick", "fix the cause at its source")

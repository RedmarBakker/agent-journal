from journal.engine.nudge import Nudge


class FaultsNudges:
    SLOW_REQUESTS = Nudge("faults", "slow_requests_to_fix", "a slow requests report is ready: {{count}} over budget, the worst {{route}} at {{ms}} ms", "read it with journal developer slowest; something may be wrong")
    SLOW_JOB = Nudge("faults", "slow_job_to_fix", "the background job {{job}} took {{seconds}} seconds for one tick", "fix what made it slow at its source")

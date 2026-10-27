from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class SchedulesNudges:
    STOP_JOB = Nudge("schedules", "stop_scheduled_job", "the user stopped your scheduled job {{job|cap=24}}", "delete it now with CronDelete, id {{job|cap=24}}", repeat=Timeout.seconds(0))

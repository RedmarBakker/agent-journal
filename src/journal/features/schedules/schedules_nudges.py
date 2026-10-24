from journal.engine.nudge import Nudge


class SchedulesNudges:
    STOP_JOB = Nudge("schedules", "stop_scheduled_job", "the user stopped your scheduled job {{job}}", "delete it now with CronDelete, id {{job}}", repeat_interval=0)

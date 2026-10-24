from journal.features.feature import Feature
from journal.features.schedules.listeners.job_record import JobRecord
from journal.features.schedules.listeners.session_jobs_end import SessionJobsEnd
from journal.features.schedules.schedules_conduct import SchedulesConduct
from journal.features.schedules.schedules_nudges import SchedulesNudges


class Schedules(Feature):
    """The prompts an agent scheduled for itself in its own program, listed in the agent bar."""

    name = "schedules"
    title = "Scheduled jobs"
    help = "Each job the agent schedules with its program's own cron tool is recorded with its schedule and prompt and listed under Scheduled in the agent bar, with when it runs next, until the agent cancels it, its session ends or, for a repeating job, seven days have passed."
    listeners = (JobRecord, SessionJobsEnd)
    conduct = (SchedulesConduct,)
    nudges = (SchedulesNudges.STOP_JOB,)

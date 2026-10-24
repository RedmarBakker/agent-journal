from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.job_stop_requested import JobStopRequested
from journal.features.schedules.schedules_nudges import SchedulesNudges


class SchedulesConduct(Conduct):
    """The schedules feature's conduct in every state: the user's stop of a job the agent scheduled is typed to that agent as a line to delete the job with its program's own tool at once."""

    def on_job_stop_requested(self, event: JobStopRequested, settings: Settings) -> Transition:
        return self.none().typing(SchedulesNudges.STOP_JOB.create(job=event.job_id)) if event.agent_session == event.session else self.none()

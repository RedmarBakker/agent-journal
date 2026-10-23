from journal.models.scheduled_job import ScheduledJob
from journal.repositories.scoped_repository import ScopedRepository


class ScheduledJobs(ScopedRepository[ScheduledJob]):
    """The jobs agents scheduled for themselves in their own programs."""

    model = ScheduledJob

    def session_jobs(self, session: str) -> list[ScheduledJob]:
        return self.selected_globally(self.query().filter(session=session, ended=False).order("id"))

    def job(self, session: str, job_id: str) -> list[ScheduledJob]:
        return self.selected_globally(self.query().filter(session=session, job_id=job_id))

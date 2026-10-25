from journal.models.scheduled_job import ScheduledJob
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.actor import Actor


class ScheduledJobs(ScopedRepository[ScheduledJob]):
    """The jobs agents scheduled for themselves in their own programs."""

    model = ScheduledJob

    def session_jobs(self, session: str) -> list[ScheduledJob]:
        return self.selected_globally(self.query().filter(session=session, ended=False).order("id"))

    def job(self, session: str, job_id: str) -> list[ScheduledJob]:
        return self.selected_globally(self.query().filter(session=session, job_id=job_id))

    def recorded(self, job: ScheduledJob, actor: Actor) -> ScheduledJob:
        with self.writing():
            existing = self.job(job.session, job.job_id)
            return existing[0] if existing else self.save(job, actor)

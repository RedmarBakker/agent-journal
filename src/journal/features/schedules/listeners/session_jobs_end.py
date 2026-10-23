from journal.events.agent.session_ended import SessionEnded
from journal.events.agent_listener import AgentListener
from journal.repositories.scheduled_jobs import ScheduledJobs
from journal.support.actor import Actor


class SessionJobsEnd(AgentListener[SessionEnded]):
    """A session's end ends every job it scheduled, since its program holds them only while it runs."""

    def __init__(self, jobs: ScheduledJobs) -> None:
        self.jobs = jobs

    def handle(self, event: SessionEnded) -> None:
        for job in self.jobs.session_jobs(event.session):
            self.jobs.save(job.ending(), Actor.system())

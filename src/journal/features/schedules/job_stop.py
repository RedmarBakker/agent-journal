from datetime import datetime, timezone

from journal.models.agent import Agent
from journal.repositories.scheduled_jobs import ScheduledJobs
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


class JobStop:
    """The user's stop of a job an agent scheduled for itself, written on the job's row: the agent is typed a line to delete the job, and the job leaves the list when its deletion is seen."""

    def __init__(self, jobs: ScheduledJobs, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.jobs = jobs

    def stop(self, agent: Agent, job_id: str, actor: Actor) -> None:
        moment = self.time_source.moment().timestamp()
        matching = [job for job in self.jobs.session_jobs(agent.session) if job.job_id == job_id and job.is_running(moment)]
        if not matching:
            raise Rejection(f"agent {agent.id} has no scheduled job {job_id}")
        self.jobs.save(matching[0].stop_requested(moment), actor)

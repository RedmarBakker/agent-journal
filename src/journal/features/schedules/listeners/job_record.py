import re

from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.models.scheduled_job import ScheduledJob
from journal.repositories.scheduled_jobs import ScheduledJobs
from journal.support.actor import Actor
from journal.support.job_cancel import JobCancel
from journal.support.job_schedule import JobSchedule

JOB_ID = re.compile(r"\b[0-9a-f]{8}\b")


class JobRecord(AgentListener[ToolFinished]):
    """A job the agent scheduled is recorded with the id its tool's answer names, and a job it cancelled is ended."""

    def __init__(self, jobs: ScheduledJobs) -> None:
        self.jobs = jobs

    def handle(self, event: ToolFinished) -> None:
        operation = event.call.operation
        if isinstance(operation, JobSchedule):
            self.scheduled(event, operation)
        if isinstance(operation, JobCancel):
            self.cancelled(event, operation)

    def scheduled(self, event: ToolFinished, schedule: JobSchedule) -> None:
        job_match = JOB_ID.search(event.output)
        if job_match:
            self.jobs.recorded(ScheduledJob(environment_id=event.environment_id, session=event.session, job_id=job_match.group(0), cron=schedule.cron, prompt=schedule.prompt, recurring=schedule.recurring), Actor.agent(event.session))

    def cancelled(self, event: ToolFinished, cancel: JobCancel) -> None:
        for job in self.jobs.job(event.session, cancel.job_id):
            self.jobs.save(job.ending(), Actor.agent(event.session))

from datetime import datetime

from journal.models.pool_job import PoolJob
from journal.models.pool_job_state import PoolJobState
from journal.repositories.repository import Repository
from journal.support.actor import Actor
from sync_server.host_request import HostRequest


class PoolJobs(Repository[PoolJob]):
    """The workers the team's pool offered this machine, one row a request, kept so a request brought by several pulls is taken up once."""

    model = PoolJob

    def arrived(self, request: HostRequest) -> None:
        if self.all_matching(request_id=request.id):
            return
        self.save(PoolJob(request_id=request.id, environment_key=request.environment_key, account_id=request.account_id, worker_id=request.body["worker_id"], profile=request.body["profile"]).arrived(), Actor.system())

    def job(self, request_id: int) -> PoolJob:
        return self.all_matching(request_id=request_id)[0]

    def today_minutes(self, moment: float) -> float:
        day_start_at = datetime.fromtimestamp(moment).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        return sum(job.minutes(moment) for job in self.all() if job.started_at >= day_start_at)

    def started_count(self) -> int:
        return len(self.all_matching(state=PoolJobState.STARTED))

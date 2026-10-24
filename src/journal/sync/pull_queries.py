from journal.repositories.pool_jobs import PoolJobs
from journal.repositories.setting_rows import SettingRows
from journal.sync.hosts import Hosts
from journal.sync.team_account import TeamAccount
from journal.version import VERSION
from sync_server.pool_slots import PoolSlots
from sync_server.pull_query import PullQuery
from journal.features.workers.workers_options import WorkersOptions


class PullQueries:
    """What this journal's pull asks the team server: the sequence it holds, how long it may wait, the environments it hosts, the worker slots this machine gives the pool with how many are free, and the version it runs."""

    def __init__(self, account: TeamAccount, hosts: Hosts, settings: SettingRows, jobs: PoolJobs) -> None:
        self.account, self.hosts, self.settings, self.jobs = account, hosts, settings, jobs

    def query(self, wait_seconds: float) -> PullQuery:
        slots = self.settings.integer(WorkersOptions.POOL_SLOTS)
        return PullQuery(self.account.sequence(), wait_seconds, self.hosts.keys(), PoolSlots(slots, max(slots - self.jobs.started_count(), 0)), VERSION)

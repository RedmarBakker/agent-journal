from journal.features.workers.feature import Workers
from journal.repositories.setting_rows import SettingRows
from journal.sync.hosts import Hosts
from journal.sync.team_account import TeamAccount
from journal.version import VERSION
from sync_server.pool_slots import PoolSlots
from sync_server.pull_query import PullQuery


class PullQueries:
    """What this journal's pull asks the team server: the sequence it holds, how long it may wait, the environments it hosts, the worker slots this machine gives the pool with how many are free, and the version it runs."""

    def __init__(self, account: TeamAccount, hosts: Hosts, settings: SettingRows) -> None:
        self.account, self.hosts, self.settings = account, hosts, settings

    def query(self, wait_seconds: float) -> PullQuery:
        slots = self.settings.integer(Workers.POOL_SLOTS)
        return PullQuery(self.account.sequence(), wait_seconds, self.hosts.keys(), PoolSlots(slots, slots), VERSION)

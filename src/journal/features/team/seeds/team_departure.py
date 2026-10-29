from journal.features.seed import Seed
from journal.features.team.support.team_join import TeamJoin
from journal.sync.team_account import TeamAccount


class TeamDeparture(Seed):
    """At boot, a journal leaves each old team account without a team version, here alone; current versioned team accounts stay joined for sync."""

    def __init__(self, account: TeamAccount, join: TeamJoin) -> None:
        self.account, self.join = account, join

    def run(self) -> None:
        while self.account.is_joined() and not self.account.team_version():
            self.join.local_departure()

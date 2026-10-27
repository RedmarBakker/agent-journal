from journal.features.seed import Seed
from journal.features.team.support.team_join import TeamJoin
from journal.sync.team_account import TeamAccount


class TeamDeparture(Seed):
    """At boot, a journal joined to a team server leaves every team it joined, here alone: the team servers are no longer used, so its sync stops and every local row stays, without asking the server."""

    def __init__(self, account: TeamAccount, join: TeamJoin) -> None:
        self.account, self.join = account, join

    def run(self) -> None:
        while self.account.is_joined():
            self.join.local_departure()

from journal.support.rejection import Rejection
from journal.sync.team_account import TeamAccount


class HubRows:
    """A row number as the CLI takes it: 12, or acme:12 for the row of the team named acme, refused when no team or more than one team has that name."""

    def __init__(self, account: TeamAccount) -> None:
        self.account = account

    def number(self, text: str) -> int:
        return self.resolve(text, [self.account.team_name()])

    @staticmethod
    def resolve(text: str, names: list[str]) -> int:
        team, colon, n = text.rpartition(":")
        if not colon:
            return int(n)
        named = [name for name in names if name and name == team]
        if not named:
            raise Rejection(f"no team is named {team}")
        if len(named) > 1:
            raise Rejection(f"more than one team is named {team}")
        return int(n)

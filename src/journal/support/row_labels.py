from journal.models.scoped import Scoped
from journal.repositories.environments import Environments
from journal.sync.team_account import TeamAccount


class RowLabels:
    """How a row is named in a line: task 57, and acme task 57 when it is a row of the joined team's hub environment."""

    def __init__(self, account: TeamAccount, environments: Environments) -> None:
        self.account, self.environments = account, environments

    def name(self, noun: str, row: Scoped) -> str:
        return f"{self.account.team_name()} {noun} {row.row_id}" if self.is_hub_row(row) else f"{noun} {row.row_id}"

    def is_hub_row(self, row: Scoped) -> bool:
        hubs = self.environments.team_chats() if self.account.team_name() else []
        return bool(hubs) and row.environment_id == hubs[0].row_id

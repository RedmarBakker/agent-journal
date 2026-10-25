from journal.config import Config
from journal.repositories.environments import Environments
from journal.sync.team_account import TEAMS_FOLDER, TeamAccount


class TeamAccounts:
    """Every team this journal has joined, one account and token each, kept in the teams folder by the team's key, the home team's first; and the person a write is stamped with, their account in the team of the environment it is made in, or in the home team."""

    def __init__(self, config: Config, environments: Environments) -> None:
        self.config, self.environments = config, environments

    def accounts(self) -> list[TeamAccount]:
        home = TeamAccount(self.config)
        others = [TeamAccount.keyed(self.config, path.stem) for path in sorted((self.config.home / TEAMS_FOLDER).glob("*.json")) if path != home.path()]
        return [home, *others] if home.is_joined() else []

    def keyed(self, key: str) -> TeamAccount:
        return next((account for account in self.accounts() if account.team_key() == key), TeamAccount(self.config))

    def person_in(self, environment_name: str) -> int:
        environments = self.environments.matching(name=environment_name)
        team_key = environments[0].team_key if environments and not environments[0].is_private() else ""
        return self.keyed(team_key).user_number()

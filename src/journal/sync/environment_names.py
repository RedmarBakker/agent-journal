from journal.models.environment import Environment
from journal.repositories.environments import Environments
from journal.sync.team_account import TeamAccount


class EnvironmentNames:
    """The environment a name a shell, a hook or a command sends stands for: the one of that name on this machine, else the one an older join renamed to the person's name before it, as main stands for jesse-main; one of that name is made when neither is there."""

    def __init__(self, environments: Environments, account: TeamAccount) -> None:
        self.environments, self.account = environments, account

    def resolved(self, name: str) -> Environment:
        matches = self.environments.matching(name=name) or self.environments.matching(name=self.account.personal_name(name))
        return matches[0] if matches else self.environments.lookup(name)

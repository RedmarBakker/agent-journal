from journal.models.environment import Environment
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.sync.hosting import Hosting
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink


class Hosts:
    """Which journal makes the writes of each environment: this one for all of them while it is in no team; in a team every journal makes its own writes in the Team chat, whose agent hears them as they are pulled, any other environment's host is the machine of the person who owns it, and one nobody owns the hosted journal. A write in an environment this journal does not host is asked of its host through the team server."""

    def __init__(self, account: TeamAccount, owners: EnvironmentOwners, environments: Environments, hosting: Hosting, link: TeamServerLink) -> None:
        self.account, self.owners, self.environments, self.hosting, self.link = account, owners, environments, hosting, link

    def keys(self) -> tuple[str, ...]:
        return tuple(environment.key for environment in self.hosted_environments())

    def hosted_environments(self) -> list[Environment]:
        if not self.account.is_joined():
            return self.environments.rows()
        unowned = self.owners.unowned() if self.hosting.is_hosted() else []
        return [*self.owners.owned(self.account.user_number()), *self.environments.sessions(), *unowned]

    def is_host(self, environment: Environment) -> bool:
        return environment.key in self.keys()

    def ask(self, environment: Environment, kind: str, body: dict, actor: Actor) -> None:
        self.link.ask_host(environment.key, kind, body, actor.number())

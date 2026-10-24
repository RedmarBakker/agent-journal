from journal.models.environment import Environment
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.sync.team_account import TeamAccount


class EnvironmentSharing:
    """An environment its owner shares with the whole team or takes back, from the command and the viewer alike: only on a journal in a team, and only by its owner."""

    def __init__(self, environments: Environments, owners: EnvironmentOwners, account: TeamAccount) -> None:
        self.environments, self.owners, self.account = environments, owners, account

    def shared(self, environment: Environment, actor: Actor) -> Environment:
        self.check(environment, actor)
        return self.environments.save(environment.shared_with_team(), actor)

    def unshared(self, environment: Environment, actor: Actor) -> Environment:
        self.check(environment, actor)
        return self.environments.save(environment.unshared(), actor)

    def check(self, environment: Environment, actor: Actor) -> None:
        if not self.account.is_joined():
            raise Rejection("this journal is in no team: an environment is shared with a team once the journal has joined one")
        if self.owners.is_colleague(actor, environment.row_id):
            raise Rejection(f"environment {environment.name} is {self.owners.owner_name(environment.row_id)}'s: only its owner shares it or takes it back")

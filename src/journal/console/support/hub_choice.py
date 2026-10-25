from contextlib import nullcontext

from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.rejection import Rejection


class HubChoice:
    """The environment a command writes in: the one it is run in, or with --team the hub environment of the joined team of that name, refused when no joined team has it."""

    def __init__(self, environments: Environments, scope: Scope) -> None:
        self.environments, self.scope = environments, scope

    def writing_in(self, team: str):
        if not team:
            return nullcontext()
        hubs = [hub for hub in self.environments.hubs() if hub.team_name == team]
        if not hubs:
            raise Rejection(f"no joined team is named {team}")
        return self.scope.environment(hubs[0].row_id)

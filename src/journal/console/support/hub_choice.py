from contextlib import nullcontext

from journal.models.environment import Environment
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.rejection import Rejection


class HubChoice:
    """The environment a command writes in: the one it is run in, or with --team the hub environment of the joined team of that name, refused when no joined team has it; a row filed for the team goes to the only hub a journal has, or to the one --team names."""

    def __init__(self, environments: Environments, scope: Scope) -> None:
        self.environments, self.scope = environments, scope

    def hub_scope(self, team: str):
        return self.scope.environment(self.hub(team).row_id) if team else nullcontext()

    def hub(self, team: str) -> Environment:
        hubs = self.environments.team_hubs(team) if team else self.environments.hubs()
        if not hubs:
            raise Rejection(f"no joined team is named {team}" if team else "there is no hub to file in: no team is joined, or the team is not on the hub yet, which journal team migrate moves it to")
        if len(hubs) > 1:
            raise Rejection("more than one team is joined: name the hub's team with --team")
        return hubs[0]

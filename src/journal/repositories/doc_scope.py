from journal.repositories.environments import Environments
from journal.repositories.scope import PROJECT, Scope


class DocScope:
    """The environments whose documents a read finds: its own, the project's and every hub's; with no environment entered, the project's and the hubs'."""

    def __init__(self, environments: Environments, scope: Scope) -> None:
        self.environments, self.scope = environments, scope

    def visible(self) -> tuple[int, ...]:
        return tuple(dict.fromkeys((self.scope.id_default(PROJECT), PROJECT, *self.environments.hub_ids())))

    def own(self) -> int:
        return self.scope.id_default(PROJECT)

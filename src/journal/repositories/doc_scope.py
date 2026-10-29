from typing import TypeVar

from journal.models.scoped import Scoped
from journal.repositories.scope import PROJECT, Scope

S = TypeVar("S", bound=Scoped)


class DocScope:
    """The environments whose documents a read finds: its own and the project's; with no environment entered, the project's."""

    def __init__(self, scope: Scope) -> None:
        self.scope = scope

    def visible(self) -> tuple[int, ...]:
        return tuple(dict.fromkeys((self.scope.id_default(PROJECT), PROJECT)))

    def own(self) -> int:
        return self.scope.id_default(PROJECT)

    def placed(self, row: S) -> S:
        return row if row.environment_id else row.with_(environment_id=self.own())

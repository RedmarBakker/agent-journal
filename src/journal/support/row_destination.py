from journal.models.scoped import Scoped
from journal.models.support.ref import Ref
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.shared_tables import SharedTables


class RowDestination:
    """Where a new row lands while the environment it is made in drives a hub plan or task, in the words a command's answer adds: on the team's hub, or kept in its environment on this machine, and nothing while it drives none; and the hub environment a row about hub rows lands in, as a report about a hub task does."""

    def __init__(self, environments: Environments, scope: Scope, tables: SharedTables) -> None:
        self.environments, self.scope, self.tables = environments, scope, tables

    def phrase(self, row: Scoped) -> str:
        return self.landing(row) if self.scope.bound() else ""

    def landing(self, row: Scoped) -> str:
        environment = self.environments.find(row.environment_id)
        return f", on the {environment.team_name} hub" if row.environment_id in self.environments.hub_ids() else f", kept in {environment.name} on this machine"

    def hub_environment_id(self, refs: list[Ref]) -> int:
        hubs = self.environments.hub_ids()
        rows = [row for ref in refs if self.tables.has(ref.type) for row in self.tables.rows(ref.type).numbered([ref.id])]
        return next((row.environment_id for row in rows if isinstance(row, Scoped) and row.environment_id in hubs), 0)

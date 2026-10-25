from journal.db.query import Query
from journal.support.actor import Actor
from journal.models.all_models import AllModels
from journal.models.environment import UNKNOWN_TEAM_KEY, Environment
from journal.models.environment_kind import EnvironmentKind
from journal.support.missing_row import MissingRow
from journal.repositories.repository import Repository


class Environments(Repository[Environment]):
    model = Environment

    def keyed(self, key: str) -> list[Environment]:
        return self.matching(key=key)

    def total(self) -> int:
        return self.counted(self.query())

    def working(self) -> list[Environment]:
        return self.selected(self.query().filter(kind=EnvironmentKind.LOCAL).order("id"))

    def team_query(self) -> Query:
        return self.query().filter_alternatives(self.query().filter_unequal("kind", EnvironmentKind.LOCAL), self.query().filter_unequal("team_key", ""))

    def hubs(self) -> list[Environment]:
        return self.matching(kind=EnvironmentKind.HUB)

    def hub_ids(self) -> tuple[int, ...]:
        with self.connection.unlisted():
            return tuple(hub.row_id for hub in self.hubs())

    def sessions(self) -> list[Environment]:
        return self.selected(self.query().filter(kind=EnvironmentKind.SESSION).order("id"))

    def team_chats(self) -> list[Environment]:
        return self.selected(self.query().filter(kind=EnvironmentKind.SESSION, branch=None).order("id"))

    def session_rows(self, names: list[str]) -> list[Environment]:
        return self.selected(self.query().filter(kind=EnvironmentKind.SESSION).filter_unequal("branch", None).filter_listed("team_name", names).order("id"))

    def keys_learnt(self, team_key: str, actor: Actor) -> None:
        for environment in self.matching(team_key=UNKNOWN_TEAM_KEY):
            self.save(environment.key_learnt(team_key), actor)

    def namesakes(self, name: str, key: str) -> list[Environment]:
        return self.selected(self.query().filter(name=name).filter_unequal("key", key).order("id"))

    def lookup(self, name: str) -> Environment:
        rows = self.matching(name=name)
        return rows[0] if rows else self.save(Environment(name=name), Actor.system())

    def entered(self, name: str) -> int:
        with self.connection.unlisted():
            return self.existing(name).row_id

    def existing(self, name: str) -> Environment:
        rows = self.matching(name=name)
        if not rows:
            raise MissingRow("environment", name)
        return rows[0]

    def wipe(self, environment: Environment, actor: Actor) -> None:
        with self.connection.transaction():
            for model in AllModels.SCOPED:
                self.purged_rows(model, Query.build(model).filter(environment_id=environment.id), actor)
            self.delete(environment, actor)

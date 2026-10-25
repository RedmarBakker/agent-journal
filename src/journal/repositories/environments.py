from journal.db.query import Query
from journal.support.actor import Actor
from journal.models.all_models import AllModels
from journal.models.environment import Environment
from journal.models.environment_kind import EnvironmentKind
from journal.support.missing_row import MissingRow
from journal.repositories.repository import Repository


class Environments(Repository[Environment]):
    model = Environment

    def keyed(self, key: str) -> list[Environment]:
        return self.matching(key=key)

    def working(self) -> list[Environment]:
        return self.selected(self.query().filter(is_team_chat=False, kind=EnvironmentKind.LOCAL).order("id"))

    def hubs(self) -> list[Environment]:
        return self.matching(kind=EnvironmentKind.HUB)

    def team_chats(self) -> list[Environment]:
        return self.selected(self.query().filter(is_team_chat=True).order("id"))

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

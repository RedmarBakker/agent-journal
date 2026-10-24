from journal.models.fact import Fact
from journal.repositories.scoped_repository import ScopedRepository


class Facts(ScopedRepository[Fact]):
    model = Fact

    def triggered(self) -> list[Fact]:
        return self.selected(self.query().filter_unlisted("trigger", [""]).order("id"))

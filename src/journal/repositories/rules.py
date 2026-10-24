from journal.models.rule import Rule
from journal.repositories.repository import Repository


class Rules(Repository[Rule]):
    model = Rule

    def triggered(self) -> list[Rule]:
        return self.selected(self.query().filter_unlisted("trigger", [""]).order("id"))

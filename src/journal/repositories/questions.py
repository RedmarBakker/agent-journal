from journal.models.question import Question
from journal.repositories.scoped_repository import ScopedRepository


class Questions(ScopedRepository[Question]):
    model = Question

    def open(self) -> list[Question]:
        return self.selected(self.query().filter_null("answer").order("id"))

    def open_count(self) -> int:
        return self.counted(self.query().filter_null("answer"))

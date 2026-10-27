from journal.models.reminder import Reminder
from journal.db.query import Query
from journal.repositories.keyword_rows import KeywordRows
from journal.repositories.scoped_repository import ScopedRepository


class Reminders(ScopedRepository[Reminder], KeywordRows):
    model = Reminder

    def standing(self) -> list[Reminder]:
        return self.selected(self.memory_query())

    def memory_query(self) -> Query:
        return self.query().filter_null("due_at")

    def triggered(self) -> list[Reminder]:
        return self.selected(self.query().filter_null("due_at").filter_unlisted("trigger", [""]).order("id"))

    def repeating(self) -> list[Reminder]:
        return self.selected(self.memory_query().filter_alternatives(self.query().filter_greater("every_minutes", 0), self.query().filter_greater("every_tool_uses", 0)).order("id"))

    def timed(self) -> list[Reminder]:
        return self.selected(self.query().filter_present("due_at").order("due_at"))

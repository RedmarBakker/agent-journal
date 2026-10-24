from journal.models.reminder import Reminder
from journal.repositories.scoped_repository import ScopedRepository


class Reminders(ScopedRepository[Reminder]):
    model = Reminder

    def standing(self) -> list[Reminder]:
        return self.selected(self.query().filter_null("due_at"))

    def triggered(self) -> list[Reminder]:
        return self.selected(self.query().filter_null("due_at").filter_unlisted("trigger", [""]).order("id"))

    def timed(self) -> list[Reminder]:
        return self.selected(self.query().filter_present("due_at").order("due_at"))

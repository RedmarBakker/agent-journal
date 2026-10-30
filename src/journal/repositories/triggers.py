from datetime import datetime

from journal.models.trigger import Trigger
from journal.repositories.repository import Repository


class Triggers(Repository[Trigger]):
    model = Trigger

    def matches(self, text: str) -> list[Trigger]:
        return [trigger for trigger in self.all() if trigger.matches(text)]

    def due(self, moment: datetime) -> list[Trigger]:
        return self.selected(self.query().filter(is_scheduled=True).filter_present("next_at").filter_less_equal("next_at", moment).order("id"))

    def listed(self) -> list[Trigger]:
        return self.selected(self.query().filter_alternatives(self.query().filter(is_scheduled=False), self.query().filter_present("next_at")).order("id"))

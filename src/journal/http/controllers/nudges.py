from journal.db.query import Query
from journal.http.controllers.controller import Controller
from journal.models.entry import Entry
from journal.repositories.entries import Entries

NUDGE = "nudge"


class NudgeController(Controller[Entry]):
    """The lines the journal typed to the agent, newest page, each an entry of its kind."""

    repository: Entries

    def __init__(self, entries: Entries) -> None:
        self.repository = entries

    def list_query(self) -> Query:
        return self.repository.query().filter(entry_type=NUDGE)


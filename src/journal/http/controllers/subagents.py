from journal.models.subagent_state import SubagentState
from journal.db.query import Query
from journal.http.controllers.controller import Controller
from journal.http.listing import SHORT_PAGE_ROWS
from journal.models.subagent import Subagent
from journal.repositories.subagents import Subagents


class SubagentController(Controller[Subagent]):
    """The subagents dispatched here, as their rows stand: one running is open, whether it was just sent, works in the background or was resumed; a list leaves each one's brief out, which its transcript opens with, ten at a time."""

    repository: Subagents
    page_rows = SHORT_PAGE_ROWS
    omitted_fields = ("brief",)

    def __init__(self, subagents: Subagents) -> None:
        self.repository = subagents

    def open_rows(self, query: Query) -> Query:
        return query.filter(state=SubagentState.ACTIVE)

    def closed_rows(self, query: Query) -> Query:
        return query.filter_unequal("state", SubagentState.ACTIVE)

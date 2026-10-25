from journal.models.subagent_state import SubagentState
from journal.db.query import Query
from journal.http.controllers.controller import Controller
from journal.models.subagent import Subagent
from journal.repositories.subagents import Subagents


class SubagentController(Controller[Subagent]):
    """The subagents dispatched here, as their rows stand: one running is open, whether it was just sent, works in the background or was resumed."""

    repository: Subagents

    def __init__(self, subagents: Subagents) -> None:
        self.repository = subagents

    def open_rows(self, query: Query) -> Query:
        return query.filter(state=SubagentState.ACTIVE)

    def closed_rows(self, query: Query) -> Query:
        return query.filter_unequal("state", SubagentState.ACTIVE)

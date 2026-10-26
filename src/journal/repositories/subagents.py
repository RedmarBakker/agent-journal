from journal.models.subagent_state import SubagentState
from journal.models.subagent import Subagent
from journal.repositories.scoped_repository import ScopedRepository


class Subagents(ScopedRepository[Subagent]):
    model = Subagent

    def session_subagents(self, session: str) -> list[Subagent]:
        return self.selected(self.query().filter(dispatcher=session).order("id"))

    def running_session_subagents(self, session: str) -> list[Subagent]:
        return self.selected(self.query().filter(dispatcher=session, state=SubagentState.ACTIVE).order("id"))

    def session_subagent(self, dispatcher: str, session: str) -> list[Subagent]:
        return self.selected(self.query().filter(dispatcher=dispatcher, session=session).order("id")) if session else []

    def newest_session_subagent(self, session: str) -> list[Subagent]:
        return self.selected(self.query().filter(dispatcher=session).order_descending("id").limit(1))

    def is_empty(self) -> bool:
        return not self.selected_globally(self.query().limit(1))

from journal.models.state_transition import StateTransition
from journal.repositories.repository import Repository
from journal.support.actor import Actor


class StateTransitions(Repository[StateTransition]):
    """The kinds of stack change counted across the project, one row a kind, the same for every environment."""

    model = StateTransition

    def counted(self, before_state: str, after_state: str, cause: str, at: float, actor: Actor) -> StateTransition:
        rows = self.matching(before_state=before_state, after_state=after_state, cause=cause)
        current = rows[0] if rows else StateTransition(before_state=before_state, after_state=after_state, cause=cause)
        return self.save(current.happened(at), actor)

    def seen_since(self, earliest: float) -> list[StateTransition]:
        return self.selected(self.query().filter_greater_equal("last_at", earliest).order("count"))

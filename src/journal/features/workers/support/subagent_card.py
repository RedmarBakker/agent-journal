from journal.support.card_outcome import CardOutcome
from dataclasses import asdict, dataclass

from journal.models.subagent import Subagent
from journal.models.subagent_state import SubagentState

# how a subagent in each state stands on its card
STATE_OUTCOMES = {SubagentState.ACTIVE.value: CardOutcome.RUNNING, SubagentState.FINISHED.value: CardOutcome.PASSED, SubagentState.FAILED.value: CardOutcome.FAILED, SubagentState.UNFINISHED.value: CardOutcome.FAILED}


@dataclass(frozen=True)
class SubagentCard:
    """What a subagent's card in the chat shows: who dispatched it, its type and model, its own session, its status at that card and why it failed."""

    session: str
    agent: int
    agent_type: str
    model: str | None
    subagent: str
    state: str
    reason: str

    @classmethod
    def built(cls, session: str, agent: int, row: Subagent, state: SubagentState, reason: str) -> "SubagentCard":
        return cls(session, agent, row.agent_type, row.model, row.session, state.value, reason)

    def as_data(self) -> dict:
        return {"kind": "subagent", **asdict(self), "outcome": str(STATE_OUTCOMES.get(self.state, CardOutcome.NONE))}

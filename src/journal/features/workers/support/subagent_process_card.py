from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.features.workers.support.subagent_card import SubagentCard
from journal.features.workers.support.subagent_card_state import SubagentCardState
from journal.features.workers.support.subagent_entries import SubagentEntries
from journal.models.message import Message
from journal.models.subagent import Subagent
from journal.models.subagent_state import SubagentState
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class SubagentProcessCard(ProcessCard):
    """The process card of a subagent's dispatch: who sent it, of which type and model and its own session once known, active until the subagent ends."""

    name = "subagent"

    def __init__(self, subagents: SubagentEntries, messages: Messages) -> None:
        self.subagents, self.messages = subagents, messages

    @staticmethod
    def key(row: Subagent) -> str:
        return f"subagent:{row.dispatch}"

    def card_contents(self, environment_id: int, session: str, agent: int, row: Subagent, actor: Actor) -> ProcessCardContents | None:
        data = {**SubagentCard.built(session, agent, row, SubagentState.ACTIVE, "").as_data(), "dispatch": row.dispatch, "active": row.is_running()}
        older = self.messages.keyed(self.key(row), actor)
        if older and all(older[0].data.get(k) == v for k, v in data.items()):
            return None
        return ProcessCardContents(self.name, environment_id, self.key(row), f"Subagent {row.agent_type}: {row.task}", data, actor, CardKind.SUBAGENTS, row.is_running(), row.task)

    def refresh(self, message: Message) -> SubagentCardState:
        row = self.subagents.dispatched(message.data["session"], message.data["dispatch"])
        return SubagentCardState(model=row.model, subagent=row.session, active=row.is_running())

from journal.engine.support.decision_return import DecisionReturn
from journal.engine.support.machine_reply import MachineReply
from journal.events.agent.agent_event import AgentEvent
from journal.repositories.agents import Agents
from journal.support.actor import Actor
from journal.support.decision import Decision


class QueuedReturn(DecisionReturn):
    """A reply to a helper, which has no terminal the journal types into: its lines wait on its row and go back with its next hook that takes lines."""

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def hook_decision(self, reply: MachineReply, event: AgentEvent) -> Decision:
        agent = self.agents.find(reply.agent.row_id)
        if event.has_hook_lines():
            self.agents.save(agent.with_(queued_lines=()), Actor.system())
            return Decision.allowed_with("\n".join(agent.queued_lines)).merged(reply.decision)
        if reply.decision.context:
            self.agents.save(agent.queued(reply.decision.context), Actor.system())
        return Decision(reply.decision.allowed, reply.decision.reason)

    def row_lines(self, reply: MachineReply) -> None:
        self.agents.save(self.agents.find(reply.agent.row_id).queued(reply.decision.context), Actor.system())

    def has_remark_queue(self) -> bool:
        return False

    def note_lines(self, lines: list[str], environment_id: int) -> str:
        return "".join(f"[journal] {line}\n" for line in lines)

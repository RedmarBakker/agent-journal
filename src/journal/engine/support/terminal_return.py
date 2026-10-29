from journal.engine.delivery import Delivery
from journal.engine.support.decision_return import DecisionReturn
from journal.engine.support.machine_reply import MachineReply
from journal.events.agent.agent_event import AgentEvent
from journal.support.decision import Decision
from journal.supervisor_link import SupervisorLink


class TerminalReturn(DecisionReturn):
    """A reply to an agent with a terminal of its own: the hook answers it, a row event's lines are typed in, and a remark waits for its terminal."""

    def __init__(self, delivery: Delivery, supervisor: SupervisorLink) -> None:
        self.delivery, self.supervisor = delivery, supervisor

    def hook_decision(self, reply: MachineReply, event: AgentEvent) -> Decision:
        return self.delivery.hook_decision(event, reply.decision)

    def row_lines(self, reply: MachineReply) -> None:
        self.delivery.lines(reply.agent.environment_id, reply.decision.context, 0.0)

    def has_remark_queue(self) -> bool:
        return True

    def note_lines(self, lines: list[str], environment_id: int) -> str:
        for line in lines:
            self.supervisor.remark(environment_id, line)
        return ""

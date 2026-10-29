from journal.engine.support.machine_reply import MachineReply
from journal.events.agent.agent_event import AgentEvent
from journal.support.decision import Decision


class DecisionReturn:
    """How a reply goes back to the agent whose floor names it: the hook's decision, the lines a row event left, and whether a remark waits in the queue for its terminal."""

    def hook_decision(self, reply: MachineReply, event: AgentEvent) -> Decision:
        raise NotImplementedError

    def row_lines(self, reply: MachineReply) -> None:
        raise NotImplementedError

    def has_remark_queue(self) -> bool:
        raise NotImplementedError

    def note_lines(self, lines: list[str], environment_id: int) -> str:
        raise NotImplementedError

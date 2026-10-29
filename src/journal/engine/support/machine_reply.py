from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.models.agent import Agent
from journal.support.decision import Decision


@dataclass(frozen=True)
class MachineReply:
    """What the state machine answers an event with, delivering nothing itself: the agent as it now stands, the bottom state of its stack, which names how the reply goes back, the decision for the hook, the lines to type into its terminal, and the remarks to queue for it; the moves the states entering and leaving the stack ask of its terminal are made as the stack is stored."""

    agent: Agent
    bottom_state: BaseState
    decision: Decision
    keystrokes: tuple[str, ...] = ()
    remarks: tuple[str, ...] = ()

    def merged(self, later: "MachineReply") -> "MachineReply":
        return MachineReply(later.agent, later.bottom_state, self.decision.merged(later.decision), (*self.keystrokes, *later.keystrokes), (*self.remarks, *later.remarks))

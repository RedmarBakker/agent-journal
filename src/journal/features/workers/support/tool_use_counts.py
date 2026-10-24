from dataclasses import dataclass

from journal.models.agent import Agent
from journal.support.recorded_call import RecordedCall
from journal.support.subagent_dispatch import SubagentDispatch

# the commands that hand work to a worker
HANDOVER_COMMANDS = ("journal worker dispatch", "journal worker send", "journal worker queue")
RESEARCH_WORKS = ("reading", "searching")


@dataclass(frozen=True)
class ToolUseCounts:
    """What an agent's tool uses say about how it shares its work, kept on its row as it works: its handovers to workers in a row with no code edit of its own, when it last handed work over, and among its newest fifty its subagent dispatches, its own reads and searches, its handovers and its own file edits."""

    consecutive_handovers: int = 0
    last_handover_at: float = 0.0
    subagent_dispatches: int = 0
    research_count: int = 0
    handovers: int = 0
    file_edits: int = 0

    @classmethod
    def counted(cls, agent: Agent) -> "ToolUseCounts":
        return cls(consecutive_handovers=agent.consecutive_handovers, last_handover_at=agent.last_handover_at,
                   subagent_dispatches=len(agent.windowed(agent.subagent_dispatch_uses)), research_count=len(agent.windowed(agent.research_uses)),
                   handovers=len(agent.windowed(agent.handover_uses)), file_edits=len(agent.windowed(agent.file_edit_uses)))

    @staticmethod
    def is_handover(call: RecordedCall) -> bool:
        return call.command.startswith(HANDOVER_COMMANDS)

    @staticmethod
    def is_subagent_dispatch(call: RecordedCall) -> bool:
        return isinstance(call.operation, SubagentDispatch)

    @staticmethod
    def is_research(call: RecordedCall) -> bool:
        return not call.writes and bool(call.read_paths or call.work in RESEARCH_WORKS)

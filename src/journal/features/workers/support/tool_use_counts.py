from dataclasses import dataclass

from journal.models.agent import WORK_WINDOW_USES, Agent
from journal.support.recorded_call import RecordedCall
from journal.support.subagent_dispatch import SubagentDispatch

# the commands that hand work to a worker
HANDOVER_COMMANDS = ("journal worker dispatch", "journal worker send", "journal worker queue")
CHECK_COMMANDS = ("journal worker check",)
MERGE_COMMANDS = ("journal worker merge",)
PROOF_COMMANDS = ("journal task show",)
RESEARCH_WORKS = ("reading", "searching")


@dataclass(frozen=True)
class ToolUseCounts:
    """What an agent's tool uses say about how it shares its work, kept on its row as it works: its handovers to workers in a row with no code edit of its own, when it last handed work over, and among its newest fifty its subagent dispatches, its own reads and searches, its handovers, its own file edits, the workers it checked and merged, the merges that followed a proof read and the tool uses made with an open task and a free place for a worker; the work mode it is counted in and how many tool uses it has made in it."""

    consecutive_handovers: int = 0
    last_handover_at: float = 0.0
    subagent_dispatches: int = 0
    research_count: int = 0
    handovers: int = 0
    file_edits: int = 0
    checked: int = 0
    merges: int = 0
    read_merges: int = 0
    idle_slots: int = 0
    mode: str = ""
    mode_uses: int = WORK_WINDOW_USES
    window_uses: int = WORK_WINDOW_USES

    @classmethod
    def counted(cls, agent: Agent) -> "ToolUseCounts":
        return cls(consecutive_handovers=agent.consecutive_handovers, last_handover_at=agent.last_handover_at,
                   subagent_dispatches=len(agent.windowed(agent.subagent_dispatch_uses)), research_count=len(agent.windowed(agent.research_uses)),
                   handovers=len(agent.windowed(agent.handover_uses)), file_edits=len(agent.windowed(agent.file_edit_uses)),
                   checked=len(agent.windowed(agent.checked_uses)), merges=len(agent.windowed(agent.merge_uses)), read_merges=len(agent.windowed(agent.read_merge_uses)), idle_slots=len(agent.windowed(agent.idle_slot_uses)),
                   mode=agent.mode, mode_uses=agent.tool_uses - agent.mode_started_use, window_uses=min(agent.tool_uses, WORK_WINDOW_USES))

    @staticmethod
    def is_handover(call: RecordedCall) -> bool:
        return call.command.startswith(HANDOVER_COMMANDS)

    @staticmethod
    def is_check(call: RecordedCall) -> bool:
        return call.command.startswith(CHECK_COMMANDS)

    @staticmethod
    def is_merge(call: RecordedCall) -> bool:
        return call.command.startswith(MERGE_COMMANDS)

    @staticmethod
    def is_proof_read(call: RecordedCall) -> bool:
        return call.command.startswith(PROOF_COMMANDS)

    @staticmethod
    def is_subagent_dispatch(call: RecordedCall) -> bool:
        return isinstance(call.operation, SubagentDispatch)

    @staticmethod
    def is_research(call: RecordedCall) -> bool:
        return not call.writes and bool(call.read_paths or call.work in RESEARCH_WORKS)

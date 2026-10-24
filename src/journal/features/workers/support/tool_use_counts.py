from dataclasses import dataclass

from journal.models.entry import Entry
from journal.support.code_files import CodeFiles
from journal.support.subagent_dispatch import SubagentDispatch

# the commands that hand work to a worker
HANDOVER_COMMANDS = ("journal worker dispatch", "journal worker send", "journal worker queue")
# the newest tool uses read for the alignment, within one page of rows, and the newest of them weighed for research
NEWEST_TOOL_USES = 90
RESEARCH_TOOL_USES = 50
RESEARCH_WORKS = ("reading", "searching")


@dataclass(frozen=True)
class ToolUseCounts:
    """What an agent's newest tool uses say about how it shares its work: its handovers to workers in a row with no code edit of its own, when it last handed work over, and among its newest fifty its subagent dispatches and its own reads and searches."""

    consecutive_handovers: int = 0
    last_handover_at: float = 0.0
    subagent_dispatches: int = 0
    research_count: int = 0

    @classmethod
    def counted(cls, starts: list[Entry]) -> "ToolUseCounts":
        handovers = [entry for entry in starts if entry.recorded_call().command.startswith(HANDOVER_COMMANDS)]
        first_code_edit = next((n for n, entry in enumerate(starts) if entry.is_write() and CodeFiles.has_code(entry.recorded_call().edited_paths)), len(starts))
        calls = [entry.recorded_call() for entry in starts[:RESEARCH_TOOL_USES]]
        return cls(consecutive_handovers=sum(1 for entry in starts[:first_code_edit] if entry in handovers),
                   last_handover_at=handovers[0].creation_time.timestamp() if handovers else 0.0,
                   subagent_dispatches=sum(1 for call in calls if isinstance(call.operation, SubagentDispatch)),
                   research_count=sum(1 for call in calls if not call.writes and (call.read_paths or call.work in RESEARCH_WORKS)))

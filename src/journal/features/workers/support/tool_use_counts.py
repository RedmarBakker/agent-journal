import re
from dataclasses import dataclass

from journal.models.agent import WORK_WINDOW_USES, Agent
from journal.models.support.agent_load import AgentLoad
from journal.support.recorded_call import RecordedCall
from journal.support.subagent_dispatch import SubagentDispatch

# the commands that hand work to a worker
HANDOVER_COMMANDS = ("journal worker dispatch", "journal worker send", "journal worker queue")
SEND_COMMANDS = ("journal worker send",)
DISPATCH_COMMANDS = ("journal worker dispatch",)
MERGE_COMMANDS = ("journal worker merge",)
PROOF_COMMANDS = ("journal task show",)
TEST_COMMANDS = ("journal suite", "pytest", "python3 -m pytest", "npm test", "npx vitest", "go test", "phpunit", "cargo test")
DONE_WHEN = re.compile(r"done[- ]when", re.IGNORECASE)
NAMED_FILES = re.compile(r"[\w-]+/[\w./-]+|\b[\w-]+\.(?:py|js|ts|vue|md|json|sh|php|go|css|html)\b|--changes")
RESEARCH_WORKS = ("reading", "searching")


@dataclass(frozen=True)
class ToolUseCounts:
    """What an agent's tool uses say about how it shares its work, kept on its row as it works: its handovers to workers in a row with no code edit of its own, when it last handed work over, and among its newest fifty its subagent dispatches, its own reads and searches, its handovers, its own file edits, its merges and those that followed a proof read and a test run, its sends to idle workers and its fresh dispatches while one sat idle, the handovers whose brief names a done-when and files, and the tool uses made while a clocked-out worker or an open task with a free place had waited too long; the work mode it is counted in and how many tool uses it has made in it; and its load as last measured, which the handling of the load is scored on, and how the models of its newest merged jobs fit them."""

    consecutive_handovers: int = 0
    last_handover_at: float = 0.0
    subagent_dispatches: int = 0
    research_count: int = 0
    handovers: int = 0
    file_edits: int = 0
    merges: int = 0
    prepared_merges: int = 0
    reuses: int = 0
    fresh_idle: int = 0
    briefed: int = 0
    late_workers: int = 0
    late_tasks: int = 0
    mode: str = ""
    mode_uses: int = WORK_WINDOW_USES
    window_uses: int = WORK_WINDOW_USES
    load: AgentLoad = AgentLoad()
    model_fits: tuple[str, ...] = ()

    @classmethod
    def counted(cls, agent: Agent) -> "ToolUseCounts":
        return cls(consecutive_handovers=agent.consecutive_handovers, last_handover_at=agent.last_handover_at,
                   subagent_dispatches=len(agent.windowed(agent.subagent_dispatch_uses)), research_count=len(agent.windowed(agent.research_uses)),
                   handovers=len(agent.windowed(agent.handover_uses)), file_edits=len(agent.windowed(agent.file_edit_uses)),
                   merges=len(agent.windowed(agent.merge_uses)), prepared_merges=len(agent.windowed(agent.prepared_merge_uses)), reuses=len(agent.windowed(agent.reuse_uses)),
                   fresh_idle=len(agent.windowed(agent.fresh_idle_uses)), briefed=len(agent.windowed(agent.briefed_uses)),
                   late_workers=len(agent.windowed(agent.late_worker_uses)), late_tasks=len(agent.windowed(agent.late_task_uses)),
                   mode=agent.mode, mode_uses=agent.tool_uses - agent.mode_started_use, window_uses=min(agent.tool_uses, WORK_WINDOW_USES), load=agent.load, model_fits=agent.model_fits)

    @staticmethod
    def is_handover(call: RecordedCall) -> bool:
        return call.command.startswith(HANDOVER_COMMANDS)

    @staticmethod
    def is_send(call: RecordedCall) -> bool:
        return call.command.startswith(SEND_COMMANDS)

    @staticmethod
    def is_dispatch(call: RecordedCall) -> bool:
        return call.command.startswith(DISPATCH_COMMANDS)

    @staticmethod
    def is_complete_brief(call: RecordedCall) -> bool:
        return bool(DONE_WHEN.search(call.command) and NAMED_FILES.search(call.command))

    @staticmethod
    def is_merge(call: RecordedCall) -> bool:
        return call.command.startswith(MERGE_COMMANDS)

    @staticmethod
    def is_proof_read(call: RecordedCall) -> bool:
        return call.command.startswith(PROOF_COMMANDS)

    @staticmethod
    def is_test_run(call: RecordedCall) -> bool:
        return call.command.startswith(TEST_COMMANDS)

    @staticmethod
    def is_subagent_dispatch(call: RecordedCall) -> bool:
        return isinstance(call.operation, SubagentDispatch)

    @staticmethod
    def is_research(call: RecordedCall) -> bool:
        return not call.writes and bool(call.read_paths or call.work in RESEARCH_WORKS)

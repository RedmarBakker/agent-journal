import re
from dataclasses import dataclass

from journal.models.agent import WORK_WINDOW_USES, Agent
from journal.models.support.agent_load import AgentLoad
from journal.models.support.report_use import ReportUse
from journal.models.support.wait_use import WaitUse
from journal.support.recorded_call import RecordedCall
from journal.support.subagent_dispatch import SubagentDispatch

# the commands that hand work to a worker
HANDOVER_COMMANDS = ("journal worker dispatch", "journal worker send", "journal worker queue")
TASK_ADDITION_COMMANDS = ("journal task create",)
TASK_COMPLETION_COMMANDS = ("journal task complete", "journal worker merge")
TEST_COMMANDS = ("journal suite", "scripts/suite.py", "pytest", "python3 -m pytest", "npm test", "npx vitest", "go test", "phpunit", "cargo test")
DONE_WHEN = re.compile(r"done[- ]when", re.IGNORECASE)
NAMED_FILES = re.compile(r"[\w-]+/[\w./-]+|\b[\w-]+\.(?:py|js|ts|vue|md|json|sh|php|go|css|html)\b|--changes")
RESEARCH_WORKS = ("reading", "searching")


@dataclass(frozen=True)
class ToolUseCounts:
    """What an agent's tool uses say about how it shares its work, kept on its row as it works: its handovers to workers in a row with no code edit of its own, when it last handed work over, and among its newest fifty its subagent dispatches, its own reads and searches, its handovers, its own file edits and the handovers whose brief names a done-when and files; the work mode it is counted in and how many tool uses it has made in it; and its load as last measured, which the handling of the load is scored on, how the models of its newest merged jobs fit them, and how the tasks of its started plans wait."""

    consecutive_handovers: int = 0
    last_handover_at: float = 0.0
    subagent_dispatches: int = 0
    research_count: int = 0
    handovers: int = 0
    file_edits: int = 0
    briefed: int = 0
    edited_lines: int = 0
    merged_lines: int = 0
    tasks_filed: int = 0
    tasks_completed: int = 0
    mode: str = ""
    mode_uses: int = WORK_WINDOW_USES
    window_uses: int = WORK_WINDOW_USES
    load: AgentLoad = AgentLoad()
    model_fits: tuple[str, ...] = ()
    waits: WaitUse = WaitUse()
    report_use: ReportUse = ReportUse()

    @classmethod
    def counted(cls, agent: Agent) -> "ToolUseCounts":
        return cls(consecutive_handovers=agent.consecutive_handovers, last_handover_at=agent.last_handover_at,
                   subagent_dispatches=len(agent.windowed(agent.subagent_dispatch_uses)), research_count=len(agent.windowed(agent.research_uses)),
                   handovers=len(agent.windowed(agent.handover_uses)), file_edits=len(agent.windowed(agent.file_edit_uses)),
                   briefed=len(agent.windowed(agent.briefed_uses)), edited_lines=sum(lines for _, lines in agent.edited_lines), merged_lines=sum(lines for _, lines in agent.merged_lines), tasks_filed=len(agent.windowed(agent.task_filed_uses)), tasks_completed=len(agent.windowed(agent.task_completed_uses)),
                   mode=agent.mode, mode_uses=agent.tool_uses - agent.mode_started_use, window_uses=min(agent.tool_uses, WORK_WINDOW_USES), load=agent.work_queue, model_fits=agent.model_fits, waits=agent.wait_use, report_use=agent.report_use)

    @staticmethod
    def is_handover(call: RecordedCall) -> bool:
        return call.command.startswith(HANDOVER_COMMANDS)

    @staticmethod
    def is_complete_brief(call: RecordedCall) -> bool:
        return bool(DONE_WHEN.search(call.command) and NAMED_FILES.search(call.command))

    @staticmethod
    def is_task_addition(call: RecordedCall) -> bool:
        return call.command.startswith(TASK_ADDITION_COMMANDS)

    @staticmethod
    def is_task_completion(call: RecordedCall) -> bool:
        return call.command.startswith(TASK_COMPLETION_COMMANDS)

    @staticmethod
    def is_subagent_dispatch(call: RecordedCall) -> bool:
        return isinstance(call.operation, SubagentDispatch)

    @staticmethod
    def is_research(call: RecordedCall) -> bool:
        return not call.writes and bool(call.read_paths or call.work in RESEARCH_WORKS)

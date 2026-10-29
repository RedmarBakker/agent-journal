from journal.features.docs.commands.doc_command import DocCommand
from journal.features.edits.feature import EditsFeature
from journal.features.memory.feature import Memory
from journal.features.tasks.feature import Tasks
from journal.features.workers.feature import Workers
from journal.features.memory.commands.rule_command import RuleCommand
from journal.features.plugins.feature import PluginsFeature
from journal.features.reports.commands.report_command import ReportCommand
from journal.features.search.commands.search_command import SearchCommand
from journal.features.shell.commands.worker_output_command import WorkerOutputCommand
from journal.features.shell.commands.reader_command import ReaderCommand
from journal.features.tasks.commands.impasse_command import ImpasseCommand
from journal.features.tasks.commands.worker_task_command import WorkerTaskCommand
from journal.features.tasks.commands.wait_command import WaitCommand
from journal.features.workers.commands.arrival_command import ArrivalCommand
from journal.features.workers.commands.departure_command import DepartureCommand
from journal.features.workers.commands.proof_command import ProofCommand
from journal.features.workers.commands.worker_tests_command import WorkerTestsCommand
from journal.features.workers.commands.todo_command import TodoCommand
from journal.features.workers.commands.worker_peer_command import WorkerPeerCommand
from journal.features.helper import Helper
from journal.features.memory.commands.memory_command import MemoryCommand
from journal.support.agent_role import AgentRole
from journal.models.alias import Alias
from journal.features.aliases.support.worker_alias_line import WorkerAliasLine

class WorkerHelper(Helper):
    """A worker: writes on one task in a worktree of its own, put to work in WorkingTask when it clocks in; the workers, tasks, edits and memory features are on for it whole, so it keeps memories of its own, and the plugins hear it."""

    role = AgentRole.WORKER
    features = (Workers, Tasks, EditsFeature, Memory, PluginsFeature)
    commands = (
        (WaitCommand, "begin"),
        (WaitCommand, "clear"),
        (ArrivalCommand, "record"),
        (DepartureCommand, "record"),
        (DocCommand, "create"),
        (DocCommand, "show"),
        (DocCommand, "update"),
        (MemoryCommand, "add"),
        (MemoryCommand, "list"),
        (MemoryCommand, "remove"),
        (MemoryCommand, "skip"),
        (MemoryCommand, "weigh"),
        (WorkerOutputCommand, "list"),
        (WorkerOutputCommand, "read"),
        (WorkerOutputCommand, "status"),
        (WorkerOutputCommand, "watch"),
        (ProofCommand, "record"),
        (ReaderCommand, "list"),
        (ReportCommand, "create"),
        (ReportCommand, "show"),
        (RuleCommand, "list"),
        (RuleCommand, "read"),
        (SearchCommand, "find"),
        (ImpasseCommand, "declare"),
        (WorkerTaskCommand, "log"),
        (WorkerTaskCommand, "show"),
        (WorkerTestsCommand, "turn"),
        (TodoCommand, "add"),
        (TodoCommand, "check"),
        (TodoCommand, "list"),
        (WorkerPeerCommand, "notify"),
        (WorkerPeerCommand, "peers"),
        (WorkerPeerCommand, "report"),
        (WorkerPeerCommand, "send"),
    )

    @classmethod
    def runs_alias(cls, alias: Alias) -> bool:
        return alias.worker_access

    @classmethod
    def alias_line(cls) -> type:
        return WorkerAliasLine

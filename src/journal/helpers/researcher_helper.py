from journal.features.docs.commands.doc_command import DocCommand
from journal.features.memory.commands.rule_command import RuleCommand
from journal.features.plans.commands.plan_command import PlanCommand
from journal.features.plugins.feature import PluginsFeature
from journal.features.reports.commands.report_command import ReportCommand
from journal.features.search.commands.search_command import SearchCommand
from journal.features.shell.commands.output_command import OutputCommand
from journal.features.tasks.commands.task_command import TaskCommand
from journal.features.workers.listeners.subagent_turn_record import SubagentTurnRecord
from journal.features.workers.states.researching import Researching
from journal.features.helper import Helper
from journal.support.agent_role import AgentRole


class ResearcherHelper(Helper):
    """A subagent of Claude Code, on its own row from its start, researching over Void: it reads and answers, runs the journal's reading commands but for memories and writes documents, reports and plans of its own, since its command names no row of its own to keep them by, reaches the plugins whose manifests name subagents, and its turns become its messages."""

    role = AgentRole.SUBAGENT
    first_state = Researching
    features = (PluginsFeature,)
    commands = (
        (DocCommand, "create"),
        (DocCommand, "update"),
        (DocCommand, "ready"),
        (DocCommand, "show"),
        (OutputCommand, "read"),
        (PlanCommand, "create"),
        (PlanCommand, "brief"),
        (PlanCommand, "phase"),
        (PlanCommand, "add"),
        (PlanCommand, "todos"),
        (PlanCommand, "ready"),
        (PlanCommand, "show"),
        (ReportCommand, "create"),
        (ReportCommand, "update"),
        (ReportCommand, "ready"),
        (ReportCommand, "show"),
        (RuleCommand, "list"),
        (RuleCommand, "read"),
        (SearchCommand, "find"),
        (TaskCommand, "list"),
        (TaskCommand, "show"),
    )
    listeners = (SubagentTurnRecord,)

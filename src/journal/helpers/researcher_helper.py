from journal.features.docs.commands.doc_command import DocCommand
from journal.features.memory.commands.fact_command import FactCommand
from journal.features.memory.commands.rule_command import RuleCommand
from journal.features.plans.commands.plan_command import PlanCommand
from journal.features.reports.commands.report_command import ReportCommand
from journal.features.search.commands.search_command import SearchCommand
from journal.features.shell.commands.output_command import OutputCommand
from journal.features.tasks.commands.task_command import TaskCommand
from journal.features.helper import Helper
from journal.support.agent_role import AgentRole


class ResearcherHelper(Helper):
    """A subagent of Claude Code: it reads and answers, and runs the journal's reading commands."""

    role = AgentRole.SUBAGENT
    commands = (
        (DocCommand, "show"),
        (FactCommand, "list"),
        (FactCommand, "read"),
        (OutputCommand, "read"),
        (PlanCommand, "show"),
        (ReportCommand, "show"),
        (RuleCommand, "list"),
        (RuleCommand, "read"),
        (SearchCommand, "find"),
        (TaskCommand, "list"),
        (TaskCommand, "show"),
    )

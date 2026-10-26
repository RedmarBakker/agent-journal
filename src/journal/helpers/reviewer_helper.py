from journal.features.docs.commands.doc_command import DocCommand
from journal.features.memory.commands.fact_command import FactCommand
from journal.features.memory.commands.rule_command import RuleCommand
from journal.features.plugins.feature import PluginsFeature
from journal.features.reports.commands.report_command import ReportCommand
from journal.features.reviewing.commands.review_command import ReviewCommand
from journal.features.reviewing.feature import ReviewingFeature
from journal.features.reviewing.states.reviewing import Reviewing
from journal.features.search.commands.search_command import SearchCommand
from journal.features.shell.commands.output_command import OutputCommand
from journal.features.tasks.commands.task_command import TaskCommand
from journal.features.helper import Helper
from journal.support.agent_role import AgentRole


class ReviewerHelper(Helper):
    """A reviewer: reads a worker's work, runs its tests and records its findings, reviewing from its first hook; the plugins hear it."""

    role = AgentRole.REVIEWER
    first_state = Reviewing
    features = (ReviewingFeature, PluginsFeature)
    commands = (
        (DocCommand, "show"),
        (FactCommand, "list"),
        (FactCommand, "read"),
        (OutputCommand, "read"),
        (ReportCommand, "show"),
        (ReviewCommand, "record"),
        (RuleCommand, "list"),
        (RuleCommand, "read"),
        (SearchCommand, "find"),
        (TaskCommand, "show"),
    )

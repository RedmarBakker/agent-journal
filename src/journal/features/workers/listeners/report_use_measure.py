from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.report_use_measuring import ReportUseMeasuring
from journal.support.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.support.actor import Actor


class ReportUseMeasure(AgentListener[ToolFinished]):
    """After each tool use of the main agent that has had reports from its workers, how often they interrupted it is measured from the reports on its row and the user's numbers, and kept there for the fitness, with what is still unrecovered of a quick report's drop."""

    def __init__(self, agents: Agents, measuring: ReportUseMeasuring) -> None:
        self.agents, self.measuring = agents, measuring

    def handle(self, event: ToolFinished) -> None:
        if event.subagent:
            return
        rows = self.agents.session_rows(event.session)
        if not rows or rows[0].role != AgentRole.MAIN or not rows[0].report_use.reports:
            return
        use = self.measuring.measured(rows[0].report_use, event.time)
        if use != rows[0].report_use:
            self.agents.save(rows[0].with_(report_use=use), Actor.system())

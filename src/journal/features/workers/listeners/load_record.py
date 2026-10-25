from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.level_entries import LevelEntries
from journal.features.workers.support.load_levels import LoadLevels
from journal.features.workers.support.load_meter import LoadMeter
from journal.features.workers.workers_options import WorkersOptions
from journal.models.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows


class LoadRecord(AgentListener[ToolFinished]):
    """After each tool use of the main agent, the level its load stood on before is recorded and its load is measured (LoadMeter)."""

    def __init__(self, agents: Agents, meter: LoadMeter, level_entries: LevelEntries, settings: SettingRows) -> None:
        self.agents, self.meter, self.level_entries, self.settings = agents, meter, level_entries, settings

    def handle(self, event: ToolFinished) -> None:
        if event.subagent:
            return
        rows = self.agents.session_rows(event.session)
        if rows and rows[0].role == AgentRole.MAIN:
            self.level_entries.record(rows[0], LoadLevels.standing(rows[0].load.rho, self.settings.decimal(WorkersOptions.WORKLOAD_FIRST_NOTICE), self.settings.decimal(WorkersOptions.WORKLOAD_NOTICE_STEP)))
            self.meter.measure(rows[0], event.time)

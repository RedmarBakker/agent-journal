from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.level_entries import LevelEntries
from journal.features.workers.support.load_levels import LoadLevels
from journal.features.workers.support.load_meter import LoadMeter
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows


class LoadRecord(AgentListener[ToolFinished]):
    """After each tool use of the main agent, the level its load stood on before is recorded and its load is measured (LoadMeter)."""

    def __init__(self, agents: Agents, meter: LoadMeter, level_entries: LevelEntries, settings: SettingRows) -> None:
        self.agents, self.meter, self.level_entries, self.settings = agents, meter, level_entries, settings

    def handle(self, event: ToolFinished) -> None:
        if event.subagent:
            return
        main = self.agents.main_row(event.session)
        if main is not None:
            self.level_entries.record(main, LoadLevels.standing(main.work_queue.rho, self.settings.decimal(WorkersOptions.WORKLOAD_FIRST_NOTICE), self.settings.decimal(WorkersOptions.WORKLOAD_NOTICE_STEP)))
            self.meter.measure(main, event.time)

from journal.events.listener import Listener
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.features.workers.workers_options import WorkersOptions
from journal.support.actor import Actor


class MergedLinesRecord(Listener[WorkerWorkMerged]):
    """The lines a worker's merge brought in are kept on its dispatcher's row, which the builder's share of its own code is weighed against, and the shas it brought in are counted, so a fast-forward of the root never counts them as the agent's own commits."""

    def __init__(self, agents: Agents, settings: SettingRows) -> None:
        self.agents, self.settings = agents, settings

    def handle(self, event: WorkerWorkMerged) -> None:
        agent = self.agents.active_main_agent(event.dispatcher) if event.dispatcher else None
        if agent is not None and event.lines:
            self.agents.rewritten(agent, Actor.system(), lambda current: current.lines_merged(event.lines, event.time, event.time - self.settings.decimal(WorkersOptions.SERIES_HOURS) * 3600).shas_counted(event.merged_shas))

from journal.events.listener import Listener
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor


class FirstReportRecord(Listener[WorkerDelivered]):
    """A clock-out that ends a job its dispatcher sent, a dispatch or a job sent, is kept on the dispatcher's row as a first report on its task; a return after a send-back never is."""

    def __init__(self, agents: Agents, settings: SettingRows) -> None:
        self.agents, self.settings = agents, settings

    def handle(self, event: WorkerDelivered) -> None:
        agent = self.agents.active_main_agent(event.worker.dispatcher) if event.worker.dispatcher else None
        if agent is None or not event.task_id or not event.first_report:
            return
        cutoff = event.time - self.settings.decimal(WorkersOptions.SERIES_HOURS) * 3600
        self.agents.rewritten(agent, Actor.system(), lambda current: current.first_reported(event.task_id, event.time, cutoff))

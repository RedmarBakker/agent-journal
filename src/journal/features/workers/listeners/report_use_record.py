from journal.events.listener import Listener
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class ReportUseRecord(Listener[WorkerDelivered]):
    """Each report a worker files at its clock-out is kept on its dispatcher's row with the tasks open for workers at that moment, which the fitness weighs; one filed within minutes of its job's start while plenty was open also costs the dispatcher a drop at once."""

    def __init__(self, workers: Workers, agents: Agents, plans: Plans, settings: SettingRows) -> None:
        self.workers, self.agents, self.plans, self.settings = workers, agents, plans, settings

    def handle(self, event: WorkerDelivered) -> None:
        worker = self.workers.find(event.worker.id)
        rows = self.agents.session_rows(worker.dispatcher) if worker.dispatcher else []
        if not rows:
            return
        open_tasks = self.plans.open_work_count()
        use = rows[0].report_use.recorded(event.time, open_tasks)
        agent = self.agents.find(rows[0].row_id)
        if self.is_quick(event.time - worker.job_start_time(), open_tasks):
            self.agents.save(agent.quick_report_dropped(use.dropped(event.time, self.settings.integer(WorkersOptions.QUICK_REPORT_DROP)), event.time, worker.id, open_tasks), Actor.system())
            return
        self.agents.save(agent.with_(report_use=use), Actor.system())

    def is_quick(self, seconds: float, open_tasks: int) -> bool:
        return seconds <= self.settings.decimal(WorkersOptions.QUICK_REPORT_MINUTES) * 60 and open_tasks >= self.settings.integer(WorkersOptions.PLENTY_OPEN)

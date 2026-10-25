from journal.features.workers.support.report_fit import ReportFit
from journal.features.workers.support.report_use_measuring import ReportUseMeasuring
from journal.features.workers.workers_options import WorkersOptions
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor


class ReportFitting:
    """Whether a worker's report choice fits the work given to it, its task in hand and its queue: one far off is told as the choice that fits, and costs its dispatcher a drop in its fitness, unless a drop of another cause is still recovering, so one cause gives one drop."""

    def __init__(self, fit: ReportFit, tasks: Tasks, agents: Agents, settings: SettingRows, measuring: ReportUseMeasuring) -> None:
        self.fit, self.tasks, self.agents, self.settings, self.measuring = fit, tasks, agents, settings, measuring

    def advice(self, worker: Worker, time: float) -> str:
        holder = Ref.build(worker)
        given = [*(self.tasks.find(task_id) for task_id in self.tasks.holder_task_ids(holder)), *self.tasks.queue(holder)]
        better = self.fit.better(worker.report_choice, given)
        if better is None:
            return ""
        line = f"worker {worker.id} reports {worker.report_choice.label()}, which does not fit its {len(given)} tasks: --report {better.label()} fits better, journal worker queue {worker.id} --report {better.label()} <task>"
        self.dropped(worker, f"worker {worker.id} reported {worker.report_choice.label()} with {len(given)} tasks given, where {better.label()} fits", time)
        return line

    def dropped(self, worker: Worker, cause: str, time: float) -> None:
        rows = self.agents.session_rows(worker.dispatcher) if worker.dispatcher else []
        if not rows or rows[0].report_use.unrecovered_points:
            return
        use = self.measuring.measured(rows[0].report_use.dropped(time, self.settings.integer(WorkersOptions.MISFIT_DROP), cause), time)
        self.agents.save(rows[0].with_(report_use=use), Actor.system())

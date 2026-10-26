from journal.features.workers.support.report_fit import ReportFit
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.tasks import Tasks


class ReportFitting:
    """Whether a worker's report choice fits the work given to it, its task in hand and its queue: one far off is told as the choice that fits."""

    def __init__(self, fit: ReportFit, tasks: Tasks) -> None:
        self.fit, self.tasks = fit, tasks

    def advice(self, worker: Worker) -> str:
        holder = Ref.build(worker)
        work_list = [*(self.tasks.find(task_id) for task_id in self.tasks.holder_task_ids(holder)), *self.tasks.queue(holder)]
        fit_choice = self.fit.better(worker.report_choice, work_list)
        if fit_choice is None:
            return ""
        line = f"worker {worker.id} reports {worker.report_choice.label()}, which does not fit its {len(work_list)} tasks: --report {fit_choice.label()} fits better, journal worker queue {worker.id} --report {fit_choice.label()} <task>"
        return line

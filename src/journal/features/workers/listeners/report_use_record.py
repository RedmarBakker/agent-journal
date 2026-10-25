from journal.events.listener import Listener
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.features.workers.support.fitness_points import FitnessPoints
from journal.features.workers.support.report_use_measuring import ReportUseMeasuring
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.workers import Workers
from journal.repositories.tasks import Tasks
from journal.repositories.proofs import Proofs
from journal.models.proof_state import ProofState
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.support.actor import Actor


class ReportUseRecord(Listener[WorkerDelivered]):
    """Each report a worker files at its clock-out is kept on its dispatcher's row with the tasks open for workers at that moment, which the fitness weighs; one filed within minutes of its job's start while plenty was open also costs the dispatcher a drop at once; the fitness is measured and its point kept right then, with no tool use of the dispatcher needed. Only a clock-out counts, the report a worker chooses: a start failure, a timeout or a stop files no clock-out, and one with a point proved not done is a worker that is stuck, left out too."""

    def __init__(self, workers: Workers, agents: Agents, plans: Plans, settings: SettingRows, points: FitnessPoints, measuring: ReportUseMeasuring, tasks: Tasks, proofs: Proofs) -> None:
        self.workers, self.agents, self.plans, self.settings, self.points, self.measuring = workers, agents, plans, settings, points, measuring
        self.tasks, self.proofs = tasks, proofs

    def handle(self, event: WorkerDelivered) -> None:
        worker = self.workers.find(event.worker.id)
        rows = self.agents.session_rows(worker.dispatcher) if worker.dispatcher else []
        if not rows or self.has_unfinished_point(worker):
            return
        open_tasks = self.plans.open_work_count()
        use = rows[0].report_use.recorded(event.time, open_tasks)
        agent = self.agents.find(rows[0].row_id)
        seconds = event.time - worker.job_start_time()
        if self.is_quick(seconds, open_tasks):
            cause = f"worker {worker.id} reported after {seconds:.0f} seconds with {open_tasks} tasks open"
            saved = self.agents.save(agent.quick_report_dropped(self.measuring.measured(use.dropped(event.time, self.settings.integer(WorkersOptions.QUICK_REPORT_DROP), cause), event.time), event.time, worker.id, open_tasks), Actor.system())
        else:
            saved = self.agents.save(agent.with_(report_use=self.measuring.measured(use, event.time)), Actor.system())
        self.points.recorded(saved, event.time)

    # a worker that clocks out with a point proved not done reports because it is stuck, which it did not choose, so it is no interruption
    def has_unfinished_point(self, worker: Worker) -> bool:
        task_ids = self.tasks.holder_task_ids(Ref.build(worker))
        return bool(task_ids) and any(proof.state == ProofState.UNFINISHED for proof in self.proofs.task_proofs(self.tasks.find(task_ids[0])))

    def is_quick(self, seconds: float, open_tasks: int) -> bool:
        return seconds <= self.settings.decimal(WorkersOptions.QUICK_REPORT_MINUTES) * 60 and open_tasks >= self.settings.integer(WorkersOptions.PLENTY_OPEN)

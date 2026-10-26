from journal.events.listener import Listener
from journal.events.rows.worker_delivered import WorkerDelivered
from journal.features.workers.support.load_items import DISPATCHES
from journal.features.workers.workers_options import WorkersOptions
from journal.models.support.ref import Ref
from journal.models.worker import REJECTION_MOVE, Worker
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor

JOB_MOVES = (*DISPATCHES, REJECTION_MOVE)


class FirstReportRecord(Listener[WorkerDelivered]):
    """A clock-out that ends a job its dispatcher sent, a dispatch or a job sent, is kept on the dispatcher's row as a first report on its task; a return after a send-back never is."""

    def __init__(self, workers: Workers, agents: Agents, tasks: Tasks, settings: SettingRows) -> None:
        self.workers, self.agents, self.tasks, self.settings = workers, agents, tasks, settings

    def handle(self, event: WorkerDelivered) -> None:
        worker = self.workers.find(event.worker.id)
        agent = self.agents.active_main_agent(worker.dispatcher) if worker.dispatcher else None
        task_ids = self.tasks.holder_task_ids(Ref.build(worker))
        if agent is None or not task_ids or not self.is_first(worker):
            return
        cutoff = event.time - self.settings.decimal(WorkersOptions.SERIES_HOURS) * 3600
        self.agents.rewritten(agent, Actor.system(), lambda current: current.first_reported(task_ids[0], event.time, cutoff))

    @staticmethod
    def is_first(worker: Worker) -> bool:
        moves = [word for word, _ in worker.moves.steps if word in JOB_MOVES]
        return bool(moves) and moves[-1] in DISPATCHES
